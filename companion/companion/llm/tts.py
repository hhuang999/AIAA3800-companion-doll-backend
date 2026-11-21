"""Aihubmix speech synthesis (Opus/PCM/WAV). Dynamic speech is not persisted to disk."""

import io
import os
import struct
import tempfile
import wave
from pathlib import Path

import httpx

from companion.content.audio import cache_key
from companion.core.config import Config


class TTSClient:
    def __init__(self, config: Config) -> None:
        self.config = config
        settings = config.settings
        key = os.environ.get(settings.llm.api_key_env)
        if not key:
            raise ValueError(f"Missing environment variable: {settings.llm.api_key_env}")
        self.client = httpx.Client(
            base_url=settings.llm.base_url, headers={"Authorization": f"Bearer {key}"}, timeout=20
        )

    def cache_key(self, text: str) -> str:
        tts = self.config.settings.tts
        return cache_key(tts.model, tts.voice, text)

    def synthesize(self, text: str, *, response_format: str | None = None) -> bytes:
        if not text or len(text) > 4096:
            raise ValueError("TTS text must contain 1-4096 characters")
        tts = self.config.settings.tts
        fmt = response_format or tts.response_format
        response = self.client.post(
            "/audio/speech",
            json={"model": tts.model, "voice": tts.voice, "input": text, "response_format": fmt},
        )
        response.raise_for_status()
        data = response.content
        if fmt == "pcm":
            if not data:
                raise ValueError("Empty TTS audio")
            # OpenAI/Aihubmix PCM output is 24kHz, mono, signed 16-bit little-endian.
            buf = io.BytesIO()
            with wave.open(buf, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(24000)
                wav_file.writeframes(data)
            data = buf.getvalue()
        self.duration(data)
        return data

    @staticmethod
    def duration(data: bytes) -> float:
        if data.startswith(b"OggS"):
            idx = data.rfind(b"OggS")
            if idx < 0 or len(data) < idx + 14:
                raise ValueError("Invalid Ogg/Opus audio")
            granule = struct.unpack_from("<q", data, idx + 6)[0]
            if granule <= 0:
                raise ValueError("Empty TTS audio")
            return granule / 48000.0
        with wave.open(io.BytesIO(data)) as audio:
            if audio.getframerate() <= 0 or audio.getnframes() == 0:
                raise ValueError("Empty TTS audio")
            return audio.getnframes() / audio.getframerate()

    def fixed_audio(self, text: str, directory: Path) -> tuple[bytes, float]:
        path = directory / f"{self.cache_key(text)}.wav"
        if path.is_file():
            data = path.read_bytes()
        else:
            # Fixed exercise and crisis assets stay RIFF WAV for wave.open duration checks.
            data = self.synthesize(text, response_format="wav")
            directory.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=directory, suffix=".tmp", delete=False) as file:
                temporary = Path(file.name)
                file.write(data)
            try:
                temporary.replace(path)
            finally:
                temporary.unlink(missing_ok=True)
        return data, self.duration(data)

    def close(self) -> None:
        self.client.close()
