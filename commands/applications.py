"""
commands/applications.py

Automações simples de abertura de aplicativos.

Todas as funções aqui SOMENTE abrem aplicativos já configurados em
config.py. Nenhuma delas aceita entrada arbitrária vinda da voz.
"""

import os
import subprocess

import config


def _open_shortcut(path: str, arguments: str = ""):
    """
    Abre um atalho (.lnk) ou executável do Windows via ShellExecute
    (os.startfile). Permite passar argumentos extras — por exemplo, um
    caminho de pasta para o VS Code abrir como workspace.

    Requer Python 3.10+ no Windows (parâmetro `arguments` de os.startfile).
    """
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f"Caminho não encontrado: {path}")

    if arguments:
        os.startfile(path, arguments=arguments)  # type: ignore[call-arg]
    else:
        os.startfile(path)


def open_development_environment():
    """Abre o Antigravity (IDE) usando o atalho configurado."""
    _open_shortcut(config.ANTIGRAVITY_PATH)


def open_notepad():
    """Abre o Bloco de Notas do Windows."""
    subprocess.Popen(["notepad.exe"])


def open_teams():
    """
    Abre o Microsoft Teams através do protocolo/URI registrado no
    Windows, evitando depender de um caminho de executável que pode
    variar entre instalações (Teams clássico x novo Teams).
    """
    for protocol in ("msteams:", "ms-teams:"):
        try:
            os.startfile(protocol)
            return
        except OSError:
            continue
    raise RuntimeError(
        "Não foi possível abrir o Teams pelo protocolo do Windows. "
        "Verifique se o Microsoft Teams está instalado."
    )
