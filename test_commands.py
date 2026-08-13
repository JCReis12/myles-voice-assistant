"""
test_commands.py

Menu simples para testar cada comando do Myles SEM precisar usar voz.

Execução:
    python test_commands.py

Este script não é obrigatório para usar o Myles — é só uma ferramenta
de apoio durante o desenvolvimento/configuração.
"""

from commands import applications, environments


def _run(label, func):
    try:
        func()
        print(f"[OK] {label}")
    except Exception as exc:
        print(f"[ERRO] {label}: {exc}")


def menu():
    options = {
        "1": ("Abrir ambiente de desenvolvimento (Antigravity)", applications.open_development_environment),
        "2": ("Abrir Teams", applications.open_teams),
        "3": ("Abrir Bloco de Notas", applications.open_notepad),
        "4": ("Abrir guias de trabalho", environments.open_work_tabs),
        "5": ("Abrir ambiente de aula de Front-end", environments.open_frontend_environment),
        "6": ("Abrir ambiente de aula de Back-end", environments.open_backend_environment),
        "0": ("Sair", None),
    }

    while True:
        print("\n--- Teste de comandos do Myles ---")
        for key, (label, _) in options.items():
            print(f"{key}. {label}")

        choice = input("Escolha uma opção: ").strip()
        if choice == "0":
            break

        entry = options.get(choice)
        if not entry:
            print("Opção inválida.")
            continue

        label, func = entry
        _run(label, func)


if __name__ == "__main__":
    menu()
