"""
config.py

Centraliza TODAS as configurações do Myles: caminhos de aplicativos,
pastas de projetos, URLs, configurações do Edge, som de ativação, voz
e reconhecimento de voz.

Nada disso deve ser hardcoded em outros arquivos — sempre importe daqui.
Os valores podem ser sobrescritos através do arquivo .env (veja .env.example).
"""

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _get(name: str, default: str = "") -> str:
    return os.getenv(name, default)


# --------------------------------------------------------------------
# Aplicativos e pastas
# --------------------------------------------------------------------
ANTIGRAVITY_PATH = _get(
    "ANTIGRAVITY_PATH", r"C:\Users\joaoc\Desktop\Antigravity IDE.lnk"
)
VSCODE_PATH = _get(
    "VSCODE_PATH", r"C:\Users\joaoc\Desktop\Visual Studio Code.lnk"
)

FRONTEND_PATH = _get(
    "FRONTEND_PATH", r"C:\Users\joaoc\Desktop\Matéria - Front-end"
)
BACKEND_PATH = _get(
    "BACKEND_PATH", r"C:\Users\joaoc\Desktop\Matéria - Back-end"
)

# --------------------------------------------------------------------
# URLs
# --------------------------------------------------------------------
CHATGPT_URL = _get("CHATGPT_URL", "https://chatgpt.com/")
FRONTEND_GITHUB_URL = _get(
    "FRONTEND_GITHUB_URL", "https://github.com/JCReis12/frontend-knowledge-base"
)
BACKEND_GITHUB_URL = _get(
    "BACKEND_GITHUB_URL", "https://github.com/JCReis12/backend-knowledge-base"
)

# --------------------------------------------------------------------
# Microsoft Edge
# --------------------------------------------------------------------
# Perfil padrão do Edge (não é trocado automaticamente pelo Myles).
EDGE_PROFILE = _get("EDGE_PROFILE", "Default")

# Caminho do executável do Edge. O padrão abaixo cobre a instalação
# mais comum no Windows 11. Ajuste no .env se o seu Edge estiver
# instalado em outro local (ex: %LOCALAPPDATA%\Microsoft\Edge\...).
EDGE_PATH = _get(
    "EDGE_PATH", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
)

# --------------------------------------------------------------------
# Som de ativação
# --------------------------------------------------------------------
# Pode ser substituído por qualquer outro .wav — basta trocar o arquivo
# em assets/ ou apontar outro caminho aqui / no .env.
ACTIVATION_SOUND = _get(
    "ACTIVATION_SOUND", os.path.join(BASE_DIR, "assets", "activation.wav")
)

# --------------------------------------------------------------------
# Text-to-Speech (voz do Myles)
# --------------------------------------------------------------------
# Palavra-chave usada para localizar uma voz masculina instalada no
# Windows (ex: "Daniel", "Duarte", "Antonio"). Se não for encontrada,
# o Myles cai para uma voz em português disponível, ou para a primeira
# voz do sistema.
TTS_VOICE_KEYWORD = _get("TTS_VOICE_KEYWORD", "Daniel")
TTS_RATE = int(_get("TTS_RATE", "175"))

# --------------------------------------------------------------------
# Reconhecimento de voz offline (Vosk)
# --------------------------------------------------------------------
# Caminho para a pasta do modelo Vosk em português já extraída.
# Baixe um modelo (ex: vosk-model-small-pt-0.3) em
# https://alphacephei.com/vosk/models e configure o caminho abaixo.
VOSK_MODEL_PATH = _get(
    "VOSK_MODEL_PATH", os.path.join(BASE_DIR, "models", "vosk-model-small-pt-0.3")
)

# Palavra de ativação exigida antes de qualquer comando.
#
# IMPORTANTE: o modelo de reconhecimento (Vosk) é treinado em português e
# não conhece o nome "Myles" — ele transcreve o que ouve foneticamente,
# geralmente como "mails" ou "miles". Por isso aceitamos várias variantes
# como válidas (veja core/command_parser.py). Se notar outras transcrições
# no log de debug do main.py, adicione-as aqui separadas por vírgula.
WAKE_WORD = _get("WAKE_WORD", "myles,mails,miles,maiuls,my less,maia,maio,maior,maiores")

# --------------------------------------------------------------------
# Interpretação de comandos (core/command_parser.py)
# --------------------------------------------------------------------
# Pontuação mínima para que uma intenção seja considerada válida. Abaixo
# disso, o Myles responde "Desculpe, não entendi o comando."
MIN_INTENT_SCORE = int(_get("MIN_INTENT_SCORE", "3"))

# Diferença mínima de pontuação entre a intenção 1ª e a 2ª colocada para
# não considerar o resultado ambíguo. Se a diferença for menor que isso,
# o Myles não executa nada (evita "chutar" entre duas intenções próximas).
MIN_SCORE_MARGIN = int(_get("MIN_SCORE_MARGIN", "2"))
