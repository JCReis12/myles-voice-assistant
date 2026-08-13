"""
test_commands.py

Menu simples para testar o Myles SEM precisar usar voz.

Execução:
    python test_commands.py

Opções:
- 1 a 6: executam as automações de verdade (abrem aplicativos).
- 7: testa a interpretação de comandos digitando frases (não abre nada).
- 8: roda uma bateria automática de testes de ambiguidade do parser
     (não abre nada) — útil para validar mudanças em command_parser.py.

Este script não é obrigatório para usar o Myles — é só uma ferramenta
de apoio durante o desenvolvimento/configuração.
"""

from commands import applications, environments
from core import command_parser


def _run(label, func):
    try:
        func()
        print(f"[OK] {label}")
    except Exception as exc:
        print(f"[ERRO] {label}: {exc}")


def _print_classification(text: str):
    """Mostra o resultado completo da interpretação para uma frase digitada."""
    wake_word, command_text = command_parser.extract_command(text)
    if wake_word is None:
        print("  -> Wake word não detectada nesta frase (nada seria executado).")
        return

    intent, scores = command_parser.classify_intent(command_text)

    print(f"  Wake word: '{wake_word}'")
    print(f"  Comando:   '{command_text}'")
    if scores:
        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        print("  Pontuação: " + ", ".join(f"{name}={score}" for name, score in ranked))
    else:
        print("  Pontuação: nenhuma intenção pontuou")
    print(f"  Intenção:  {intent or '(nenhuma — \"Desculpe, não entendi o comando\")'}")


def test_parser_interactive():
    """Modo interativo: digite frases e veja como o parser interpreta cada uma."""
    print("\n--- Teste de interpretação (digite frases, 'sair' para voltar) ---")
    print("Exemplo: Myles, prepara meu ambiente de frontend\n")
    while True:
        text = input("Frase> ").strip()
        if not text or text.lower() in ("sair", "voltar", "0"):
            break
        _print_classification(text)
        print()


# Casos de teste de ambiguidade — cobrem os cenários do documento de
# requisitos (intenções específicas vencendo intenções genéricas, wake
# word em variações fonéticas, comandos curtos de desligamento, etc).
AMBIGUITY_TEST_CASES = [
    ("Myles, abre meu ambiente de frontend", "open_frontend_environment"),
    ("Myles, abre meu ambiente de backend", "open_backend_environment"),
    ("Myles, abre meu ambiente de desenvolvimento", "open_development_environment"),
    ("Myles, abre minhas ferramentas de trabalho", "open_work_tabs"),
    ("Myles, abre o Teams", "open_teams"),
    ("Myles, abre o bloco de notas", "open_notepad"),
    ("Myles, desligar", "shutdown"),
    ("Myles, abre meu ambiente de desenvolvimento frontend", "open_frontend_environment"),
    ("Myles, abre meu ambiente de desenvolvimento backend", "open_backend_environment"),
    ("Myles, prepara meu ambiente de frontend", "open_frontend_environment"),
    ("Myles, prepara meu ambiente de backend", "open_backend_environment"),
    ("Myles, abre as coisas da aula de frontend", "open_frontend_environment"),
    ("Myles, abre as coisas da aula de backend", "open_backend_environment"),
    ("Myles, quero estudar frontend", "open_frontend_environment"),
    ("Myles, quero estudar backend", "open_backend_environment"),
    ("Myles, abre as ferramentas para a aula de frontend", "open_frontend_environment"),
    ("Myles, pode abrir o Teams", "open_teams"),
    ("Myles, inicia o Teams", "open_teams"),
    ("Myles, quero abrir o Teams", "open_teams"),
    ("Myles, sair", "shutdown"),
    ("Myles, pode parar", "shutdown"),
    ("Mails abrir bloco de notas", "open_notepad"),  # wake word foneticamente diferente
]


def run_ambiguity_tests():
    """Roda a bateria de testes de interpretação e imprime PASS/FAIL para cada um."""
    print("\n--- Testes automáticos de interpretação (não abre nenhum aplicativo) ---")
    passed = 0
    for text, expected in AMBIGUITY_TEST_CASES:
        wake_word, command_text = command_parser.extract_command(text)
        intent = command_parser.parse_intent(command_text) if wake_word else None
        status = "PASS" if intent == expected else "FAIL"
        if status == "PASS":
            passed += 1
        print(f"[{status}] '{text}' -> esperado={expected} obtido={intent}")
    print(f"\n{passed}/{len(AMBIGUITY_TEST_CASES)} testes passaram.")


def menu():
    options = {
        "1": ("Abrir ambiente de desenvolvimento (Antigravity)", applications.open_development_environment),
        "2": ("Abrir Teams", applications.open_teams),
        "3": ("Abrir Bloco de Notas", applications.open_notepad),
        "4": ("Abrir guias de trabalho", environments.open_work_tabs),
        "5": ("Abrir ambiente de aula de Front-end", environments.open_frontend_environment),
        "6": ("Abrir ambiente de aula de Back-end", environments.open_backend_environment),
        "7": ("Testar interpretação de comandos (digitar frases, não abre nada)", test_parser_interactive),
        "8": ("Rodar testes automáticos de ambiguidade (não abre nada)", run_ambiguity_tests),
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
        if choice in ("7", "8"):
            func()  # modos interativos/relatório próprios, sem o wrapper _run
        else:
            _run(label, func)


if __name__ == "__main__":
    menu()
