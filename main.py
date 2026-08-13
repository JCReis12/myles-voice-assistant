"""
main.py

Ponto de entrada do Myles.

Execução:
    python main.py

Comportamento:
    1. Inicializa voz (TTS) e reconhecimento de voz offline.
    2. Informa que está online e passa a ouvir continuamente.
    3. Para cada frase reconhecida, verifica se contém a wake word
       ("Myles"); se sim, toca o som de ativação, interpreta a
       intenção e executa a função correspondente.
    4. Responde por voz o resultado da ação.
    5. Encerra ao ouvir "Myles, desligar" ou com Ctrl+C no terminal.

O Myles NÃO é uma IA generativa: apenas reconhece um conjunto fixo de
comandos pré-programados (veja core/command_parser.py e commands/).
"""

import sys

import config
from core.voice import VoiceOutput, play_activation_sound
from core.listener import SpeechListener
from core import command_parser
from core import executor


def print_banner():
    print("=" * 40)
    print("           MYLES ONLINE")
    print("           Listening...")
    print("=" * 40)


def main():
    voice = VoiceOutput(voice_keyword=config.TTS_VOICE_KEYWORD, rate=config.TTS_RATE)

    try:
        listener = SpeechListener(model_path=config.VOSK_MODEL_PATH)
    except RuntimeError as exc:
        print(str(exc))
        sys.exit(1)

    print_banner()
    voice.speak("Myles online. Aguardando comandos.")

    try:
        for phrase in listener.listen():
            print(f"[debug] Vosk reconheceu: '{phrase}'")
            command_text = command_parser.extract_command(phrase)
            if command_text is None:
                # Wake word ("Myles") não detectada nesta frase — ignora.
                continue

            play_activation_sound(config.ACTIVATION_SOUND)
            intent = command_parser.parse_intent(command_text)

            if intent == "shutdown":
                voice.speak("Até mais.")
                break

            response = executor.execute(intent)
            voice.speak(response)

    except KeyboardInterrupt:
        print("\n[Myles] Encerrado manualmente (Ctrl+C).")
    finally:
        listener.stop()


if __name__ == "__main__":
    main()
