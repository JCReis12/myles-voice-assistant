"""
core/listener.py

Reconhecimento de voz OFFLINE utilizando Vosk.

O sounddevice captura áudio do dispositivo de ENTRADA PADRÃO do Windows
automaticamente — funciona tanto com o microfone interno quanto com um
headset/fone, sem qualquer alteração de código quando o dispositivo padrão
muda (basta trocar o padrão nas configurações de som do Windows).
"""

import json
import sys
import queue

import sounddevice as sd
import vosk


class SpeechListener:
    """Escuta o microfone continuamente e produz frases finais reconhecidas."""

    def __init__(self, model_path: str, samplerate: int = 16000):
        vosk.SetLogLevel(-1)  # silencia logs internos do Vosk/Kaldi

        try:
            self.model = vosk.Model(model_path)
        except Exception as exc:
            raise RuntimeError(
                "Não foi possível carregar o modelo de reconhecimento de voz "
                f"em '{model_path}'.\n"
                "Baixe um modelo em português em "
                "https://alphacephei.com/vosk/models, extraia a pasta e "
                "configure VOSK_MODEL_PATH no arquivo .env."
            ) from exc

        self.samplerate = samplerate
        self._queue: "queue.Queue[bytes]" = queue.Queue()
        self._recognizer = vosk.KaldiRecognizer(self.model, self.samplerate)
        self._stream = None

    def _callback(self, indata, frames, time_info, status):
        if status:
            print(f"[listener] status: {status}", file=sys.stderr)
        self._queue.put(bytes(indata))

    def start(self):
        """Abre o stream de áudio usando o dispositivo de entrada padrão do Windows."""
        self._stream = sd.RawInputStream(
            samplerate=self.samplerate,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=self._callback,
        )
        self._stream.start()

    def stop(self):
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

    def listen(self):
        """
        Generator que fica ouvindo o microfone e produz (yield) uma frase
        de cada vez, sempre que o reconhecedor identifica o fim de uma fala.
        """
        self.start()
        try:
            while True:
                data = self._queue.get()
                if self._recognizer.AcceptWaveform(data):
                    result = json.loads(self._recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        yield text
        finally:
            self.stop()
            