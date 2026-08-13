"""
commands/browser.py

Automação de abertura de páginas SEMPRE no Microsoft Edge, com o
perfil configurado — não depende do navegador padrão do Windows
(por isso não usamos webbrowser.open()).
"""

import subprocess

import config


def open_edge(urls, new_window: bool = True):
    """
    Abre uma ou mais URLs no Microsoft Edge, usando o perfil padrão
    configurado em config.EDGE_PROFILE. Quando `new_window` é True,
    todas as URLs são abertas como abas de uma mesma janela nova.
    """
    if not urls:
        return

    cmd = [config.EDGE_PATH, f"--profile-directory={config.EDGE_PROFILE}"]
    if new_window:
        cmd.append("--new-window")
    cmd.extend(urls)

    subprocess.Popen(cmd)
