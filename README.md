# Myles — Assistente de Automação Desktop por Voz

Myles é um **assistente pessoal de automação desktop controlado por voz** para
Windows 11. Ele **não é uma IA generativa** e **não tem comportamento
autônomo**: é um interpretador de comandos de voz com um conjunto fixo de
intenções pré-programadas.

```
voz → reconhecimento → intenção → função → automação → resposta por voz
```

---

## 1. Estrutura do projeto

```
myles-voice-assistant/
│
├── main.py                  # Ponto de entrada (python main.py)
├── config.py                # TODA a configuração centralizada
├── test_commands.py         # Menu para testar comandos sem usar voz
├── .env                     # Suas configurações locais (não versionar)
├── .env.example             # Modelo de configuração
├── requirements.txt         # Dependências Python
├── .gitignore
│
├── core/
│   ├── listener.py          # Captura e reconhecimento de voz offline (Vosk)
│   ├── command_parser.py    # Detecção da wake word "Myles" + intenções
│   ├── executor.py          # Liga intenção → função de automação
│   └── voice.py             # Text-to-Speech e som de ativação
│
├── commands/
│   ├── applications.py      # Antigravity, Teams, Bloco de Notas
│   ├── browser.py           # Abertura do Microsoft Edge
│   └── environments.py      # Rotinas compostas (guias de trabalho, aulas)
│
├── assets/
│   └── activation.wav       # Som tocado quando "Myles" é detectado
│
└── models/
    └── vosk-model-small-pt-0.3/   # Modelo de voz (você baixa, não incluso)
```

---

## 2. Pré-requisitos

- Windows 11
- Python 3.10 ou superior (necessário para `os.startfile(..., arguments=...)`,
  usado para abrir o VS Code direto numa pasta específica)
- Um microfone configurado como dispositivo de entrada padrão do Windows
  (interno ou headset — o Myles usa sempre o que estiver definido como
  padrão em **Configurações > Som**)
- Microsoft Edge instalado
- (Opcional, mas recomendado) uma voz masculina em português instalada no
  Windows — veja seção 7

---

## 3. Instalação

### 3.1. Criar e ativar o ambiente virtual

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3.2. Instalar as dependências

```powershell
pip install -r requirements.txt
```

> **pywin32**: em algumas instalações é necessário rodar
> `python .venv\Scripts\pywin32_postinstall.py -install` após o `pip install`
> caso alguma funcionalidade do Windows apresente erro de importação. Na V1
> ele é usado apenas como suporte a bibliotecas do ecossistema Windows; se
> não for necessário no seu ambiente, pode ignorar esse passo.

### 3.3. Baixar o modelo de reconhecimento de voz (Vosk, offline)

O reconhecimento de voz é 100% offline usando a biblioteca **Vosk**. Isso
significa que você precisa baixar um modelo de linguagem em português uma
única vez (ele não é baixado automaticamente pelo pip):

1. Acesse https://alphacephei.com/vosk/models
2. Baixe um modelo em português, por exemplo `vosk-model-small-pt-0.3`
   (~50 MB, mais rápido, um pouco menos preciso) ou um modelo maior se
   quiser mais precisão.
3. Extraia o `.zip` dentro da pasta `models/`, de forma que o resultado
   seja algo como:
   ```
   models/vosk-model-small-pt-0.3/
   ```
4. Confirme que `VOSK_MODEL_PATH` no `.env` aponta para essa pasta.

**Limitação conhecida**: modelos pequenos do Vosk são mais rápidos, porém
podem errar em frases muito longas ou com ruído de fundo. Para a V1, isso é
aceitável, já que os comandos são curtos e o vocabulário é pequeno.

### 3.4. Configurar o `.env`

```powershell
copy .env.example .env
```

Edite o `.env` e ajuste os caminhos para a sua máquina (veja seção 6 para a
lista completa de variáveis).

---

## 4. Executando o Myles

```powershell
python main.py
```

Você verá:

```
========================================
           MYLES ONLINE
           Listening...
========================================
```

O Myles fica ouvindo continuamente. Exemplo de uso:

```
Você:  "Myles, abra o ambiente de desenvolvimento"
Myles: *som de ativação*
Myles: "Ambiente de desenvolvimento aberto."
```

### Desligando

Por voz:

```
"Myles, desligar"
```

Myles responde "Até mais." e encerra o processo.

Manualmente, no terminal: `Ctrl+C`.

---

## 5. Testando comandos sem usar voz

```powershell
python test_commands.py
```

Isso abre um menu numerado no terminal para disparar cada ação
individualmente (Antigravity, Teams, Notepad, guias de trabalho, ambiente de
front-end, ambiente de back-end) sem precisar falar nada.

---

## 6. Configuração (tudo centralizado em `config.py` / `.env`)

| Variável | O que controla |
|---|---|
| `ANTIGRAVITY_PATH` | Atalho (.lnk) do Antigravity IDE |
| `VSCODE_PATH` | Atalho (.lnk) do VS Code |
| `FRONTEND_PATH` | Pasta do projeto de Front-end |
| `BACKEND_PATH` | Pasta do projeto de Back-end |
| `CHATGPT_URL` | URL do ChatGPT |
| `FRONTEND_GITHUB_URL` | URL do repositório GitHub de Front-end |
| `BACKEND_GITHUB_URL` | URL do repositório GitHub de Back-end |
| `EDGE_PROFILE` | Perfil do Edge usado (padrão: `Default`) |
| `EDGE_PATH` | Caminho do executável do Edge |
| `ACTIVATION_SOUND` | Caminho do som de ativação (.wav) |
| `TTS_VOICE_KEYWORD` | Nome/trecho do nome da voz masculina do Windows |
| `TTS_RATE` | Velocidade da fala |
| `VOSK_MODEL_PATH` | Pasta do modelo de reconhecimento de voz |
| `WAKE_WORD` | Palavra de ativação (padrão: `myles`) |

Nunca é necessário editar código Python para trocar caminhos, URLs, o som de
ativação ou a voz — tudo isso é feito pelo `.env`.

### Trocando o som de ativação

Basta substituir o arquivo `assets/activation.wav` por outro `.wav` (mesmo
nome) ou apontar `ACTIVATION_SOUND` no `.env` para outro arquivo. Se o
arquivo não existir, o Myles continua funcionando normalmente, apenas sem
tocar som.

---

## 7. Sobre a voz (TTS)

A V1 usa **pyttsx3**, que no Windows utiliza o motor **SAPI5** já embutido
no sistema operacional — sem instalação extra, sem internet.

O Windows 11 já vem com pelo menos uma voz em português (geralmente
**Maria**, feminina). Para ter uma voz **masculina em português**
(ex: Daniel, Duarte), pode ser necessário instalá-la manualmente:

1. **Configurações do Windows > Hora e Idioma > Fala**
2. Em "Vozes gerenciadas", clique em **Adicionar vozes**
3. Adicione um pacote de voz em Português (Brasil) que inclua uma voz
   masculina

Depois disso, defina `TTS_VOICE_KEYWORD` no `.env` com um trecho do nome da
voz instalada (ex: `Daniel`). Se a voz configurada não for encontrada, o
Myles cai automaticamente para qualquer voz em português disponível e, na
ausência de uma, para a primeira voz do sistema — o programa nunca quebra
por causa disso.

O motor de TTS fica isolado em `core/voice.py` (classe `VoiceOutput`), então
trocar de engine no futuro (ex: por um TTS mais avançado) significa reescrever
apenas esse arquivo.

---

## 8. Sobre o reconhecimento de voz

A V1 usa **Vosk**, uma engine de reconhecimento de fala totalmente offline.
A captura de áudio é feita com **sounddevice**, que usa automaticamente o
dispositivo de entrada **padrão do Windows** — ao trocar de microfone
interno para headset (ou vice-versa), basta que o Windows aponte esse
dispositivo como padrão; nenhuma alteração de código é necessária.

**Estratégia de wake word**: em vez de um wake-word engine dedicado (que
adicionaria bastante complexidade a uma V1), o Myles ouve frases completas
continuamente e verifica se alguma variante de "myles" aparece no texto
reconhecido (veja seção 8.1 sobre por que existem várias variantes).

### 8.1. Por que várias variantes de "Myles"?

O modelo Vosk usado é treinado em português e não conhece o nome "Myles" —
ele transcreve o som foneticamente, geralmente como **"mails"** ou
**"miles"**. Por isso `WAKE_WORD` no `.env` aceita uma lista separada por
vírgula (`myles,mails,miles,maiuls,my less`). Se notar outra variante nos
logs de debug, adicione-a ali — não precisa mexer em código.

### 8.2. Interpretação de comandos por palavras-chave e pontuação

A partir da versão atual, o Myles **não exige mais frases quase idênticas**
às cadastradas. A interpretação (em `core/command_parser.py`) funciona por
**palavras-chave com peso, combinações e prioridade** — continua 100%
determinístico, sem IA, LLM ou qualquer modelo generativo:

1. O texto reconhecido é normalizado (minúsculas, sem acento, sem
   pontuação, e variações como `front-end`/`front end`/`frontend` viram
   um único token).
2. A wake word é removida do início.
3. Cada intenção soma pontos para cada palavra-chave do comando que
   aparecer em `INTENT_KEYWORDS` (palavras mais decisivas têm peso maior;
   palavras genéricas como "ambiente" têm peso baixo de propósito).
4. Combinações de palavras (`INTENT_COMBOS`) dão um bônus extra — por
   exemplo, "ambiente" + "frontend" juntos valem mais do que a soma das
   duas palavras isoladas.
5. Comandos curtos (1-2 palavras após a wake word, como "Myles, sair" ou
   "Myles, Teams") recebem um bônus adicional, já que são naturalmente
   mais deliberados e menos ambíguos que uma palavra solta no meio de uma
   frase longa.
6. Intenções específicas suprimem intenções genéricas relacionadas
   (`SPECIFICITY_OVERRIDES`) — por exemplo, se a palavra "frontend" ou
   "backend" aparece, `OPEN_DEVELOPMENT` e `OPEN_WORK_TABS` são
   descartados, para que "ambiente de desenvolvimento frontend" resulte
   em `OPEN_FRONTEND`, não em `OPEN_DEVELOPMENT`.
7. A intenção com maior pontuação vence, desde que:
   - a pontuação seja pelo menos `MIN_INTENT_SCORE` (padrão: 3);
   - a diferença para a 2ª colocada seja pelo menos `MIN_SCORE_MARGIN`
     (padrão: 2) — caso contrário, o resultado é tratado como ambíguo e
     nada é executado.

Ambos os limiares são configuráveis no `.env`.

**Exemplo prático** — "Myles, prepara meu ambiente de frontend":

```
[DEBUG] Vosk reconheceu: 'mails prepara meu ambiente de frontend'
[DEBUG] Wake word: 'mails'
[DEBUG] Comando: 'prepara meu ambiente de frontend'
[DEBUG] Pontuação: open_frontend_environment=9
[DEBUG] Executando: open_frontend_environment
```

**Limitação conhecida**: como o sistema não entende gramática, uma
palavra-chave de peso alto (ex: "frontend", "teams") em qualquer lugar de
uma frase — mesmo incidental — pode disparar a intenção correspondente
(ex: "essa reunião sobre frontend foi cancelada" ainda ativa
`OPEN_FRONTEND`). Isso é intencional: pesos baixos o suficiente para
evitar esse caso também impediriam comandos curtos e diretos como
"Myles, frontend". Se isso incomodar no seu uso, ajuste os pesos em
`INTENT_KEYWORDS` (`core/command_parser.py`) ou aumente `MIN_INTENT_SCORE`
no `.env`.

Pequenas variações de fala ("abra"/"abre"/"pode abrir"/"quero abrir") são
naturalmente aceitas porque a maioria dos verbos não entra na pontuação —
o que importa são as palavras-chave que identificam a intenção.

### 8.3. Testando a interpretação sem usar voz

```powershell
python test_commands.py
```

- Opção **7**: digite frases livremente e veja a wake word detectada, o
  comando extraído, a pontuação de cada intenção e a intenção vencedora —
  sem abrir nenhum aplicativo.
- Opção **8**: roda uma bateria automática de casos de teste (inclusive os
  casos de ambiguidade entre `OPEN_DEVELOPMENT`/`OPEN_FRONTEND`/
  `OPEN_BACKEND`/`OPEN_WORK_TABS`) e mostra quantos passaram — útil sempre
  que você ajustar pesos ou adicionar uma intenção nova.

### 8.4. Adicionando uma nova intenção na V2

Exemplo: "Myles, abre meu projeto de Data Engineering".

1. Em `core/command_parser.py`, adicione a intenção em `INTENT_KEYWORDS`:
   ```python
   "open_data_engineering_project": {
       "dados": 2, "data": 2, "engenharia": 3, "engineering": 3,
       "pipeline": 3, "etl": 4, "ambiente": 1,
   },
   ```
2. (Opcional) Adicione uma combinação em `INTENT_COMBOS`:
   ```python
   ("open_data_engineering_project", {"ambiente", "dados"}, 2),
   ```
3. (Opcional) Se a nova intenção deve vencer alguma genérica (como
   `OPEN_DEVELOPMENT`), registre em `SPECIFICITY_OVERRIDES`.
4. Crie a função de automação em `commands/` e registre-a em
   `core/executor.py` (`ACTIONS` e `RESPONSES`), exatamente como já é
   feito hoje — nada muda no executor.
5. Rode `python test_commands.py` (opção 7 ou 8) para validar antes de
   testar por voz.

---

## 9. Segurança

O Myles executa **somente** ações explicitamente programadas em
`commands/`. Ele nunca:

- executa comandos arbitrários de terminal vindos da voz;
- interpreta uma frase qualquer como comando de shell;
- apaga, cria ou modifica arquivos além de abrir aplicativos/pastas/URLs
  pré-configurados;
- instala programas automaticamente.

---

## 10. Comandos da V1

| Comando de voz | Ação |
|---|---|
| "Myles, abra o ambiente de desenvolvimento" | Abre o Antigravity |
| "Myles, abra o Teams" | Abre o Microsoft Teams |
| "Myles, abra o bloco de notas" | Abre o Notepad |
| "Myles, abra as guias de trabalho" | Edge (ChatGPT) + Antigravity em nova janela |
| "Myles, abra as abas para a aula de frontend" | Edge (ChatGPT + GitHub Front-end) + VS Code na pasta de Front-end |
| "Myles, abra as abas para a aula de backend" | Edge (ChatGPT + GitHub Back-end) + VS Code na pasta de Back-end |
| "Myles, desligar" | Encerra o Myles |

---

## 11. Adicionando novos comandos (preparação para V2)

A arquitetura foi pensada para crescer sem reescrever o projeto. O passo a
passo completo, com o novo sistema de palavras-chave e pontuação, está na
seção **8.4**. Resumo rápido:

1. **Crie a função de automação** em um módulo de `commands/` (ou crie um
   novo módulo, ex: `commands/data_engineering.py`).
2. **Registre a intenção** em `core/command_parser.py`, adicionando uma
   nova chave em `INTENT_KEYWORDS` com as palavras-chave e pesos (e,
   opcionalmente, uma combinação em `INTENT_COMBOS`).
3. **Ligue a intenção à função** em `core/executor.py`, adicionando entradas
   em `ACTIONS` (obrigatório) e `RESPONSES` (frase de confirmação falada).
4. Se o novo comando precisar de caminhos/URLs, adicione-os em `config.py`
   e no `.env` — nunca hardcode dentro de `commands/`.
5. Valide com `python test_commands.py` (opções 7 e 8) antes de testar por
   voz.

Comandos como "Myles, faça o commit" (automação Git) seguem exatamente o
mesmo padrão e ficam reservados para uma versão futura, conforme
planejado — a V1 propositalmente não implementa nenhuma automação Git.

---

## 12. Rodando o Myles em segundo plano (sem depender do terminal)

Na V1, o uso padrão é `python main.py` com o terminal aberto. Caso queira
rodar sem uma janela de terminal visível no futuro, duas opções comuns:

- Usar `pythonw.exe` no lugar de `python.exe` (não abre console):
  ```powershell
  pythonw.exe main.py
  ```
- Empacotar com uma ferramenta como PyInstaller (`--noconsole`), fora do
  escopo da V1.

---

## 13. Inicialização automática com o Windows (documentado, mas DESATIVADO)

A V1 **não ativa** inicialização automática — o comportamento padrão
continua sendo executar manualmente `python main.py`.

Para habilitar isso no futuro, duas abordagens simples:

### Opção A — Pasta de Inicialização do Windows

1. Crie um arquivo `iniciar_myles.bat` com o conteúdo:
   ```bat
   @echo off
   cd /d "C:\caminho\para\myles-voice-assistant"
   call .venv\Scripts\activate.bat
   pythonw.exe main.py
   ```
2. Pressione `Win + R`, digite `shell:startup` e pressione Enter.
3. Coloque um atalho para `iniciar_myles.bat` dentro dessa pasta.

### Opção B — Agendador de Tarefas do Windows

1. Abra o **Agendador de Tarefas**.
2. Crie uma nova tarefa com gatilho "Ao fazer logon".
3. Ação: executar `iniciar_myles.bat` (mesmo script da Opção A).

Para **desativar**, basta remover o atalho da pasta de inicialização (Opção
A) ou desabilitar/excluir a tarefa (Opção B).

---

## 14. Limitações conhecidas da V1

- O reconhecimento de voz offline (Vosk) é mais sensível a ruído de fundo do
  que serviços online — para melhor precisão, use um ambiente relativamente
  silencioso ou um headset com microfone direcional.
- A detecção da wake word é baseada em busca de texto na frase reconhecida,
  não em um wake-word engine dedicado; frases muito longas contendo "myles"
  em outro contexto poderiam, em teoria, disparar o assistente — aceitável
  para o uso pessoal da V1.
- A qualidade da voz masculina em português depende das vozes SAPI5
  instaladas no Windows (veja seção 7).
