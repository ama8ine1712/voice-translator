import queue
import sys
import time
from dataclasses import dataclass
from typing import Generator, Optional

import numpy as np
import sounddevice as sd
import webrtcvad

from .config import AppConfig


@dataclass
class AudioSegment:
	pcm16: bytes
	sample_rate: int
	duration_ms: int


def float_to_int16_pcm(audio_float: np.ndarray) -> bytes:
	clipped = np.clip(audio_float, -1.0, 1.0)
	pcm = (clipped * 32767.0).astype(np.int16)
	return pcm.tobytes()


class VADRecorder:
	def __init__(self, config: AppConfig):
		self.config = config
		self.vad = webrtcvad.Vad(self.config.aggressiveness)
		self.sample_rate = self.config.sample_rate
		self.frame_ms = self.config.frame_ms
		self.frame_bytes = int(self.sample_rate * self.frame_ms / 1000) * 2  # 16-bit mono
		self._q: queue.Queue[bytes] = queue.Queue()
		self._stream: Optional[sd.InputStream] = None

	def _callback(self, indata, frames, time_info, status):
		if status:
			print(f"[audio] {status}", file=sys.stderr)
		pcm_bytes = float_to_int16_pcm(indata[:, 0])
		self._q.put(pcm_bytes)

	def start(self):
		self._stream = sd.InputStream(
			channels=1,
			samplerate=self.sample_rate,
			dtype="float32",
			callback=self._callback,
		)
		self._stream.start()

	def stop(self):
		if self._stream is not None:
			self._stream.stop()
			self._stream.close()
			self._stream = None

	def segments(self) -> Generator[AudioSegment, None, None]:
		"""Yield speech segments using VAD with padding and max duration."""
		ring = bytearray()
		triggered = False
		speech_bytes = bytearray()
		padding_frames = int(self.config.padding_ms / self.frame_ms)
		padding_ring: list[bool] = []
		start_time: Optional[float] = None
		max_bytes = int(self.sample_rate * self.config.max_segment_ms / 1000) * 2

		while True:
			chunk = self._q.get()
			ring.extend(chunk)
			while len(ring) >= self.frame_bytes:
				frame = bytes(ring[: self.frame_bytes])
				ring = ring[self.frame_bytes :]
				is_speech = False
				try:
					is_speech = self.vad.is_speech(frame, self.sample_rate)
				except Exception:
					is_speech = False

				if not triggered:
					padding_ring.append(is_speech)
					if len(padding_ring) > padding_frames:
						padding_ring.pop(0)
					if sum(padding_ring) > 0.9 * len(padding_ring):
						triggered = True
						start_time = time.time()
						speech_bytes.extend(frame)
				else:
					speech_bytes.extend(frame)
					too_long = len(speech_bytes) >= max_bytes
					end_condition = not is_speech and sum(padding_ring) < 0.1 * len(padding_ring)
					padding_ring.append(is_speech)
					if len(padding_ring) > padding_frames:
						padding_ring.pop(0)
					if too_long or end_condition:
						dur_ms = int((len(speech_bytes) / 2) / self.sample_rate * 1000)
						yield AudioSegment(pcm16=bytes(speech_bytes), sample_rate=self.sample_rate, duration_ms=dur_ms)
						triggered = False
						speech_bytes.clear()
						padding_ring.clear()
