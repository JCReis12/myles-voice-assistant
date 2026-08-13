"""
core/listener.py

Reconhecimento de voz OFFLINE utilizando Vosk.

O sounddevice captura áudio do dispositivo de ENTRADA PADRÃO do Windows
automaticamente — funciona tanto com o microfone interno quanto com um
headset/fone, sem qualquer alteração de código quando o dispositivo padrão
muda (basta trocar o padrão nas configurações de som do Windows).
"""

import array
import json
import sys
import queue

import sounddevice as sd
import vosk


class SpeechListener:
    """Escuta o microfone continuamente e produz frases finais reconhecidas."""

    def __init__(self, model_path: str, samplerate: int = 16000, debug_audio_level: bool = True):
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

        # Diagnóstico temporário: imprime um medidor de nível de áudio no
        # console para confirmar se o microfone está realmente entregando
        # som ao Python (útil para depurar problemas de permissão/dispositivo).
        # Pode ser desligado passando debug_audio_level=False.
        self._debug_audio_level = debug_audio_level
        self._chunk_count = 0

    def _callback(self, indata, frames, time_info, status):
        if status:
            print(f"[listener] status: {status}", file=sys.stderr)
        self._queue.put(bytes(indata))

        if self._debug_audio_level:
            self._chunk_count += 1
            # blocksize=8000 a 16kHz ~= 0.5s por chunk; imprime a cada ~2s
            if self._chunk_count % 4 == 0:
                samples = array.array("h")
                samples.frombytes(bytes(indata))
                peak = max((abs(s) for s in samples), default=0)
                bar = "#" * min(50, peak // 200)
                print(f"[listener] nível de áudio: {peak:5d} {bar}")

    def start(self):
        """Abre o stream de áudio usando o dispositivo de entrada padrão do Windows."""
        try:
            device_info = sd.query_devices(kind="input")
            print(f"[listener] Dispositivo de entrada padrão: {device_info['name']}")
        except Exception as exc:
            print(f"[listener] Não foi possível consultar o dispositivo padrão de entrada: {exc}")

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
