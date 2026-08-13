"""
core/command_parser.py

Camada de interpretação de comandos. Sistema DETERMINÍSTICO baseado em
palavras-chave, combinações de palavras, pontuação e prioridade entre
intenções — SEM IA generativa, LLM, API externa, embeddings ou qualquer
modelo de machine learning.

Fluxo:
    texto reconhecido (Vosk)
        -> normalização
        -> remoção da wake word ("Myles"/variantes)
        -> extração das palavras do comando
        -> pontuação de cada intenção (palavras-chave + combinações)
        -> prioridade: intenções específicas suprimem intenções genéricas
        -> intenção vencedora, respeitando limiar mínimo de confiança
           e margem mínima de desempate

Para adicionar uma nova intenção na V2 (ex: OPEN_DATA_ENGINEERING):
1. Adicione uma entrada em INTENT_KEYWORDS com as palavras-chave e pesos.
2. (Opcional) Adicione combinações de palavras em INTENT_COMBOS para dar
   um bônus quando aparecerem juntas (ex: "ambiente" + "dados").
3. (Opcional) Se a nova intenção for mais específica que alguma intenção
   genérica já existente, registre isso em SPECIFICITY_OVERRIDES.
4. Crie a função correspondente em commands/.
5. Registre a função em core/executor.py (ACTIONS e RESPONSES).
Não é necessário mexer no restante do parser.
"""

import re
import unicodedata

import config

# --------------------------------------------------------------------
# Wake word
# --------------------------------------------------------------------
# O modelo de reconhecimento é em português e não conhece o nome "Myles" —
# ele transcreve o som foneticamente (ex: "mails", "miles"). Por isso
# comparamos contra uma lista de variantes em vez de um texto exato.
WAKE_WORDS = [w.strip().lower() for w in config.WAKE_WORD.split(",") if w.strip()]

# --------------------------------------------------------------------
# Confiança mínima / desempate (centralizados em config.py / .env)
# --------------------------------------------------------------------
MIN_INTENT_SCORE = config.MIN_INTENT_SCORE
MIN_SCORE_MARGIN = config.MIN_SCORE_MARGIN

# Comandos muito curtos (1-2 palavras após a wake word) são, por natureza,
# mais deliberados e menos ambíguos do que uma palavra-chave perdida no
# meio de uma frase longa. Por isso qualquer intenção que já tenha
# pontuado recebe um bônus extra quando o comando é curto — isso permite
# que comandos diretos como "Myles, sair" ou "Myles, Teams" funcionem sem
# precisar de pesos artificialmente altos que causariam falsos positivos
# em frases mais longas contendo a mesma palavra incidentalmente.
SOLO_COMMAND_MAX_WORDS = 2
SOLO_COMMAND_BONUS = 4

# --------------------------------------------------------------------
# Aliases fonéticos (mesma ideia da wake word, aplicada às palavras-chave)
# --------------------------------------------------------------------
# O Vosk é um modelo de português e não conhece termos técnicos em inglês
# como "frontend"/"backend" — ele tenta encaixar o som em palavras
# parecidas que conhece (ex: "frontend" vira "fonte" ou "fronte"). Cada
# entrada aqui é tratada como sinônimo exato da palavra-canônica à
# direita ANTES da pontuação, então INTENT_KEYWORDS, INTENT_COMBOS e
# SPECIFICITY_OVERRIDES continuam funcionando normalmente sem precisar
# ser duplicados.
#
# ATENÇÃO: só adicione aqui palavras que o Vosk realmente produziu nos
# seus testes (veja o log "[DEBUG] Vosk reconheceu: ..." no main.py).
# Palavras muito comuns do português (ex: "fonte" também significa
# "font"/"nascente") aumentam o risco de disparar o comando errado em
# frases que não têm nada a ver com frontend/backend — nesse projeto o
# risco é aceitável porque é um assistente pessoal de uso único, mas vale
# saber da troca.
PRONUNCIATION_ALIASES = {
    "fonte": "frontend",
    "fronte": "frontend",
    # Confirmado no log de debug do usuário — "backend" sendo transcrito
    # como "pequim" (apareceu 2x seguidas na mesma sessão de testes).
    "pequim": "backend",
    # "teams" virando "time" (palavra comum) ou "tim" (nome próprio/marca).
    "time": "teams",
    "tim": "teams",
}


def _apply_pronunciation_aliases(text: str) -> str:
    return " ".join(
        PRONUNCIATION_ALIASES.get(word, word) for word in text.split()
    )


def _normalize(text: str) -> str:
    """
    Minúsculas, sem acentos, sem pontuação, espaços colapsados, e
    variações de escrita comuns unificadas em um único token
    (front-end / front end / frontend -> frontend; idem para backend).
    Também aplica os aliases fonéticos de PRONUNCIATION_ALIASES.
    """
    text = text.lower().strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    text = re.sub(r"\bfront[\s]?end\b", "frontend", text)
    text = re.sub(r"\bback[\s]?end\b", "backend", text)
    text = _apply_pronunciation_aliases(text)

    return text


def extract_command(text: str):
    """
    Procura alguma variante da wake word (ex: "myles", "mails", "miles")
    na frase reconhecida, usando limite de palavra (word boundary) para
    não casar substrings dentro de outra palavra.

    Retorna uma tupla (wake_word_encontrada, texto_do_comando). Se
    nenhuma variante aparecer na frase, retorna (None, None) e a frase
    deve ser ignorada pelo chamador.
    """
    norm = _normalize(text)

    best_match = None
    matched_wake = None
    for wake in WAKE_WORDS:
        pattern = r"\b" + re.escape(wake) + r"\b"
        match = re.search(pattern, norm)
        if match and (best_match is None or match.start() < best_match.start()):
            best_match = match
            matched_wake = wake

    if best_match is None:
        return None, None

    command_text = norm[best_match.end():].strip()
    command_text = re.sub(r"^,?\s*", "", command_text)
    return matched_wake, command_text


# --------------------------------------------------------------------
# Palavras-chave por intenção
# --------------------------------------------------------------------
# Peso maior = palavra mais específica/decisiva para aquela intenção.
# Palavras muito genéricas (ex: "ambiente") recebem peso baixo de
# propósito, para não conseguirem disparar uma ação sozinhas.
INTENT_KEYWORDS = {
    "shutdown": {
        "desligar": 5, "desligue": 5, "desliga": 5,
        "encerrar": 5, "encerre": 5, "encerra": 5,
        "finalizar": 4, "finalize": 4,
        "parar": 1, "pare": 1,
        "sair": 1,
    },
    "open_teams": {
        "teams": 5,
        "team": 4,
        "reuniao": 2,
        "microsoft": 1,
    },
    "open_notepad": {
        "bloco": 3,
        "notas": 3,
        "notepad": 5,
    },
    "open_development_environment": {
        "desenvolvimento": 3,
        "desenvolver": 2,
        "programacao": 2,
        "programar": 2,
        "antigravity": 5,
        "ambiente": 1,
    },
    "open_work_tabs": {
        "trabalho": 3,
        "trabalhar": 2,
        "ferramentas": 2,
        "guias": 1,
        "abas": 1,
        "ambiente": 1,
    },
    "open_frontend_environment": {
        "frontend": 5,
        "aula": 1,
        "estudar": 2,
        "estudo": 2,
        "materia": 1,
        "preparar": 1,
        "prepara": 1,
        "ambiente": 1,
    },
    "open_backend_environment": {
        "backend": 5,
        "aula": 1,
        "estudar": 2,
        "estudo": 2,
        "materia": 1,
        "preparar": 1,
        "prepara": 1,
        "ambiente": 1,
    },
}

# --------------------------------------------------------------------
# Combinações de palavras (bônus)
# --------------------------------------------------------------------
# Cada combo é (intenção, {palavras necessárias}, bônus). TODAS as
# palavras do conjunto precisam aparecer no comando para o bônus valer.
INTENT_COMBOS = [
    ("open_frontend_environment", {"ambiente", "frontend"}, 2),
    ("open_frontend_environment", {"aula", "frontend"}, 2),
    ("open_backend_environment", {"ambiente", "backend"}, 2),
    ("open_backend_environment", {"aula", "backend"}, 2),
    ("open_development_environment", {"ambiente", "desenvolvimento"}, 2),
    ("open_work_tabs", {"ambiente", "trabalho"}, 1),
    ("open_work_tabs", {"ferramentas", "trabalho"}, 1),
]

# --------------------------------------------------------------------
# Prioridade entre intenções (específica vence genérica)
# --------------------------------------------------------------------
# Cada entrada é (palavras_gatilho, intenções_genéricas). Quando QUALQUER
# palavra do gatilho aparece literalmente no comando, todas as intenções
# do grupo genérico são suprimidas antes da decisão final. Usamos a
# presença da palavra (não a pontuação da intenção) para evitar que uma
# palavra-chave genérica compartilhada (ex: "ambiente") dispare a
# supressão por engano. Isso garante que "ambiente de desenvolvimento
# frontend" resulte em OPEN_FRONTEND (e não em OPEN_DEVELOPMENT), e que
# "ferramentas para a aula de frontend" resulte em OPEN_FRONTEND (e não
# em OPEN_WORK_TABS) — mas que "ambiente de desenvolvimento" sozinho
# continue resultando normalmente em OPEN_DEVELOPMENT.
SPECIFICITY_OVERRIDES = [
    (
        {"frontend", "backend"},
        {"open_development_environment", "open_work_tabs"},
    ),
]


def score_intents(command_text: str):
    """
    Calcula a pontuação de cada intenção para o texto do comando (já sem
    a wake word). Retorna um dicionário {intenção: pontuação} somente
    com intenções que pontuaram > 0 após todas as regras (palavras-chave,
    combinações, bônus de comando curto e prioridade/supressão).
    """
    norm = _normalize(command_text)
    words = set(norm.split())

    scores = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        total = sum(weight for word, weight in keywords.items() if word in words)
        if total > 0:
            scores[intent] = total

    for intent, required_words, bonus in INTENT_COMBOS:
        if required_words.issubset(words):
            scores[intent] = scores.get(intent, 0) + bonus

    if words and len(words) <= SOLO_COMMAND_MAX_WORDS:
        for intent in list(scores.keys()):
            scores[intent] += SOLO_COMMAND_BONUS

    for trigger_words, generic_group in SPECIFICITY_OVERRIDES:
        if trigger_words & words:
            for generic_intent in generic_group:
                scores.pop(generic_intent, None)

    return scores


def classify_intent(command_text: str):
    """
    Decide a intenção vencedora a partir da pontuação.

    Retorna (intent_ou_None, scores_dict). `intent` é None quando:
    - nenhuma intenção pontuou;
    - a melhor pontuação não atinge MIN_INTENT_SCORE;
    - a diferença entre a 1ª e a 2ª colocada é menor que MIN_SCORE_MARGIN
      (ambiguidade — o Myles não "chuta" entre duas intenções próximas).
    """
    scores = score_intents(command_text)
    if not scores:
        return None, scores

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    best_intent, best_score = ranked[0]

    if best_score < MIN_INTENT_SCORE:
        return None, scores

    if len(ranked) > 1:
        _, second_score = ranked[1]
        if (best_score - second_score) < MIN_SCORE_MARGIN:
            return None, scores

    return best_intent, scores


def parse_intent(command_text: str):
    """
    Atalho usado pelo restante do projeto (core/executor.py): retorna
    apenas o nome da intenção vencedora, ou None.
    """
    intent, _ = classify_intent(command_text)
    return intent
