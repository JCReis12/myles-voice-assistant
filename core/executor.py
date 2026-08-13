"""
core/executor.py

Liga cada intenção reconhecida à função de automação correspondente
(em commands/) e produz a resposta em voz. Nenhum comando arbitrário é
executado aqui — apenas as ações explicitamente registradas em ACTIONS.

Para adicionar uma nova intenção na V2:
1. Crie a função em commands/<algum_modulo>.py.
2. Importe-a aqui.
3. Adicione uma entrada em ACTIONS e (opcionalmente) uma frase de
   resposta em RESPONSES.
"""

from commands import applications, environments

RESPONSES = {
    "open_development_environment": "Ambiente de desenvolvimento aberto.",
    "open_teams": "Teams aberto.",
    "open_notepad": "Bloco de notas aberto.",
    "open_work_tabs": "Abrindo suas ferramentas de trabalho.",
    "open_frontend_environment": "Ambiente de front-end aberto.",
    "open_backend_environment": "Ambiente de back-end aberto.",
}

ACTIONS = {
    "open_development_environment": applications.open_development_environment,
    "open_teams": applications.open_teams,
    "open_notepad": applications.open_notepad,
    "open_work_tabs": environments.open_work_tabs,
    "open_frontend_environment": environments.open_frontend_environment,
    "open_backend_environment": environments.open_backend_environment,
}


def execute(intent: str) -> str:
    """
    Executa a ação associada à intenção e retorna a frase de resposta.
    Nunca lança exceção para fora — qualquer erro vira uma resposta
    genérica de falha, sem detalhes técnicos falados em voz alta.
    """
    action = ACTIONS.get(intent)
    if action is None:
        return "Desculpe, não entendi o comando."

    try:
        action()
        return RESPONSES.get(intent, "Feito.")
    except Exception as exc:
        print(f"[executor] Erro ao executar '{intent}': {exc}")
        return "Não consegui executar esse comando."
