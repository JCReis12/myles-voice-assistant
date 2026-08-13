"""
commands/environments.py

Rotinas compostas: combinam navegador + editor + IDE para montar um
"ambiente de trabalho" com um único comando de voz.

Estas funções são o ponto natural para crescer na V2 — por exemplo,
"abra meu projeto de Data Engineering" seria uma nova função aqui,
seguindo o mesmo padrão.
"""

import config
from commands import applications, browser


def open_work_tabs():
    """
    'Myles, abra as guias de trabalho'
    Edge -> ChatGPT
    Antigravity -> nova janela
    """
    browser.open_edge([config.CHATGPT_URL], new_window=True)
    applications._open_shortcut(config.ANTIGRAVITY_PATH)


def open_frontend_environment():
    """
    'Myles, abra as abas para a aula de frontend'
    Edge -> ChatGPT, GitHub (front-end)
    VS Code -> pasta Matéria - Front-end
    """
    browser.open_edge(
        [config.CHATGPT_URL, config.FRONTEND_GITHUB_URL], new_window=True
    )
    applications._open_shortcut(
        config.VSCODE_PATH, arguments=f'"{config.FRONTEND_PATH}"'
    )


def open_backend_environment():
    """
    'Myles, abra as abas para a aula de backend'
    Edge -> ChatGPT, GitHub (back-end)
    VS Code -> pasta Matéria - Back-end
    """
    browser.open_edge(
        [config.CHATGPT_URL, config.BACKEND_GITHUB_URL], new_window=True
    )
    applications._open_shortcut(
        config.VSCODE_PATH, arguments=f'"{config.BACKEND_PATH}"'
    )
