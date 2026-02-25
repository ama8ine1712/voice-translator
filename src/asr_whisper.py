import queue
import threading
import tempfile
import os
from dataclasses import dataclass
from typing import Generator, Optional
import sounddevice as sd
import soundfile as sf
import numpy as np
import whisper

from .config import AppConfig


@dataclass
class ASRResult:
	text: str
	language: Optional[str]


class WhisperASR:
	def __init__(self, config: AppConfig):
		self.config = config
		self._q: "queue.Queue[ASRResult]" = queue.Queue()
		self._started = False
		self._thread: Optional[threading.Thread] = None
		self._recording = False
		self._audio_buffer = []
		
		# Load Whisper model
		print(f"Loading Whisper model: {config.whisper_model_size}")
		self.model = whisper.load_model(config.whisper_model_size)
		print("Whisper model loaded successfully!")

	def _record_audio(self):
		"""Record audio in chunks and process when speech ends"""
		def audio_callback(indata, frames, time, status):
			if status:
				print(f"Audio callback status: {status}")
			if self._recording:
				self._audio_buffer.append(indata.copy())

		# Start recording
		self._recording = True
		stream = sd.InputStream(
			samplerate=self.config.sample_rate,
			channels=1,
			callback=audio_callback,
			blocksize=int(self.config.sample_rate * 0.1)  # 100ms blocks
		)
		
		stream.start()
		
		try:
			while self._started:
				# Record for 3 seconds or until silence
				import time
				time.sleep(3.0)
				
				if self._audio_buffer:
					# Convert buffer to numpy array
					audio_data = np.concatenate(self._audio_buffer, axis=0)
					
					# Save to temporary file
					with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
						sf.write(tmp_file.name, audio_data, self.config.sample_rate)
						
						try:
							# Transcribe with Whisper
							result = self.model.transcribe(tmp_file.name, language="en")
							text = result["text"].strip()
							
							if text:
								print(f"Transcribed: {text}")
								self._q.put(ASRResult(text=text, language="en"))
						except Exception as e:
							print(f"Transcription error: {e}")
						finally:
							# Clean up temp file
							os.unlink(tmp_file.name)
					
					# Clear buffer
					self._audio_buffer = []
					
		finally:
			stream.stop()
			stream.close()

	def _run(self):
		self._started = True
		self._record_audio()

	def start(self):
		if self._thread is not None:
			return
		self._thread = threading.Thread(target=self._run, daemon=True)
		self._thread.start()

	def stop(self):
		self._started = False
		self._recording = False
		if self._thread is not None:
			self._thread.join(timeout=3)
			self._thread = None

	def results(self) -> Generator[ASRResult, None, None]:
		while True:
			res = self._q.get()
			yield res





