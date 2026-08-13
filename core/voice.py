"""
core/voice.py

Saída de voz (Text-to-Speech) e reprodução do som de ativação.

V1: utiliza pyttsx3, que no Windows usa o motor SAPI5 já embutido no
sistema — não depende de internet nem de instalação de TTS pesado.

O motor de TTS fica isolado nesta classe para que, futuramente, seja
possível trocá-lo (ex: por outro engine offline) sem alterar o resto
do projeto — basta reimplementar VoiceOutput mantendo o método speak().
"""

import os

import pyttsx3

try:
    import winsound
except ImportError:  # pragma: no cover - só existe no Windows
    winsound = None


class VoiceOutput:
    def __init__(self, voice_keyword: str = "", rate: int = 175):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self._select_voice(voice_keyword)

    def _select_voice(self, keyword: str):
        """
        Tenta selecionar uma voz cujo nome contenha `keyword` (ex: "Daniel").
        Se não encontrar, tenta uma voz em português; caso contrário usa a
        primeira voz disponível no Windows.

        Nota: o Windows 11 traz vozes em português (ex: "Maria" - feminina)
        por padrão. Vozes masculinas em português (ex: "Daniel", "Duarte")
        podem precisar ser instaladas em
        Configurações > Hora e Idioma > Voz > Adicionar vozes.
        """
        voices = self.engine.getProperty("voices")
        chosen = None
        keyword = (keyword or "").lower()

        if keyword:
            for v in voices:
                if keyword in v.name.lower():
                    chosen = v
                    break

        if chosen is None:
            for v in voices:
                name = v.name.lower()
                langs = " ".join(str(l) for l in (getattr(v, "languages", []) or []))
                if "portug" in name or "brazil" in name or "pt-br" in langs.lower():
                    chosen = v
                    break

        if chosen is None and voices:
            chosen = voices[0]

        if chosen is not None:
            self.engine.setProperty("voice", chosen.id)

    def speak(self, text: str):
        print(f"[Myles] {text}")
        self.engine.say(text)
        self.engine.runAndWait()


def play_activation_sound(path: str):
    """
    Toca o som de ativação. Se o arquivo não existir ou não estiver no
    Windows, o Myles continua funcionando normalmente (não quebra).
    """
    if winsound is None:
        return
    if path and os.path.isfile(path):
        try:
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as exc:
            print(f"[voice] Não foi possível tocar o som de ativação: {exc}")
    else:
        print("[voice] Som de ativação não encontrado — continuando sem som.")
