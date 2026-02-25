import io
from typing import Optional

import numpy as np
import sounddevice as sd
import soundfile as sf


def play_wav_bytes(wav_bytes: bytes, device: Optional[int] = None):
	with io.BytesIO(wav_bytes) as bio:
		data, samplerate = sf.read(bio, dtype="float32")
		sd.play(data, samplerate=samplerate, device=device)
		sd.wait()


def play_pcm16_mono(pcm16: bytes, sample_rate: int, device: Optional[int] = None):
	pcm = np.frombuffer(pcm16, dtype=np.int16).astype("float32") / 32768.0
	sd.play(pcm, samplerate=sample_rate, device=device)
	sd.wait()
