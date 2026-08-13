"""
core/command_parser.py

Camada de interpretação de comandos. NÃO utiliza IA generativa nem
modelos de linguagem — apenas normalização de texto e correspondência
com frases pré-definidas por intenção.

Para adicionar uma nova intenção na V2, basta:
1. Adicionar uma nova entrada em INTENTS com as variações de frase aceitas.
2. Criar a função correspondente em commands/.
3. Registrar a função em core/executor.py (ACTIONS e RESPONSES).
"""

import re
import unicodedata

import config

WAKE_WORD = config.WAKE_WORD.lower()


def _normalize(text: str) -> str:
    """Minúsculas, sem acentos, sem pontuação, espaços colapsados."""
    text = text.lower().strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# Cada intenção lista variações naturais de como o comando pode ser dito.
# A ordem não importa — a frase mais longa encontrada no texto vence,
# o que evita que "teams" capture acidentalmente outro comando maior.
INTENTS = {
    "shutdown": [
        "desligar", "pode desligar", "desliga", "encerrar", "encerre",
        "finalizar", "pode encerrar",
    ],
    "open_development_environment": [
        "abra o ambiente de desenvolvimento",
        "abre o ambiente de desenvolvimento",
        "abrir o ambiente de desenvolvimento",
        "abra ambiente de desenvolvimento",
        "pode abrir o ambiente de desenvolvimento",
        "pode abrir ambiente de desenvolvimento",
        "ambiente de desenvolvimento",
    ],
    "open_teams": [
        "abra o teams",
        "abre o teams",
        "abrir o teams",
        "pode abrir o teams",
        "abra teams",
        "abrir teams",
        "teams",
    ],
    "open_notepad": [
        "abra o bloco de notas",
        "abre o bloco de notas",
        "abrir o bloco de notas",
        "pode abrir o bloco de notas",
        "abra bloco de notas",
        "bloco de notas",
    ],
    "open_work_tabs": [
        "abra as guias de trabalho",
        "abre as guias de trabalho",
        "abrir as guias de trabalho",
        "pode abrir as guias de trabalho",
        "abra guias de trabalho",
        "guias de trabalho",
    ],
    "open_frontend_environment": [
        "abra as abas para a aula de frontend",
        "abra as abas para aula de frontend",
        "abre as abas para a aula de frontend",
        "abrir as abas para a aula de frontend",
        "abas da aula de frontend",
        "abas para a aula de frontend",
        "aula de frontend",
        "aula de front end",
        "ambiente de frontend",
        "ambiente de front end",
    ],
    "open_backend_environment": [
        "abra as abas para a aula de backend",
        "abra as abas para aula de backend",
        "abre as abas para a aula de backend",
        "abrir as abas para a aula de backend",
        "abas da aula de backend",
        "abas para a aula de backend",
        "aula de backend",
        "aula de back end",
        "ambiente de backend",
        "ambiente de back end",
    ],
}


def extract_command(text: str):
    """
    Procura a wake word ("myles") na frase reconhecida. Se encontrada,
    retorna o texto normalizado que vem depois dela (o comando em si).
    Se a wake word não aparecer, retorna None e a frase é ignorada.
    """
    norm = _normalize(text)
    idx = norm.find(WAKE_WORD)
    if idx == -1:
        return None
    command_text = norm[idx + len(WAKE_WORD):].strip()
    command_text = re.sub(r"^,?\s*", "", command_text)
    return command_text


def parse_intent(command_text: str):
    """Retorna o nome da intenção reconhecida, ou None se nada corresponder."""
    if not command_text:
        return None
    norm = _normalize(command_text)

    best_intent = None
    best_len = 0
    for intent, phrases in INTENTS.items():
        for phrase in phrases:
            if phrase in norm and len(phrase) > best_len:
                best_intent = intent
                best_len = len(phrase)
    return best_intent
