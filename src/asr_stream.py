import queue
import threading
from dataclasses import dataclass
from typing import Generator, Optional

from .config import AppConfig


@dataclass
class ASRResult:
	text: str
	language: Optional[str]


class AzureStreamingASR:
	def __init__(self, config: AppConfig, auto_languages: Optional[list[str]] = None):
		import azure.cognitiveservices.speech as speechsdk
		self.speechsdk = speechsdk
		self.config = config
		self._q: "queue.Queue[ASRResult]" = queue.Queue()
		self._recognizer = None
		self._started = False
		self._thread: Optional[threading.Thread] = None
		self.auto_languages = auto_languages or [
			"en-US", "en-GB", "el-GR", "es-ES", "fr-FR", "hi-IN"
		]

	def _run(self):
		speechsdk = self.speechsdk
		from .speech_utils import create_speech_config
		
		speech_conf = create_speech_config(self.config)
		if speech_conf is None:
			return  # stop gracefully if config not created
		audio_conf = speechsdk.audio.AudioConfig(use_default_microphone=True)
		auto_conf = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=self.auto_languages)
		recognizer = speechsdk.SpeechRecognizer(
			speech_config=speech_conf,
			audio_config=audio_conf,
			auto_detect_source_language_config=auto_conf,
		)
		self._recognizer = recognizer

		def recognized(evt):
			if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
				detail = speechsdk.AutoDetectSourceLanguageResult(evt.result)
				lang = detail.language if detail and hasattr(detail, "language") else None
				self._q.put(ASRResult(text=evt.result.text, language=lang))

		recognizer.recognized.connect(recognized)
		recognizer.start_continuous_recognition_async().get()
		self._started = True

		while self._started:
			self.speechsdk.time.sleep(0.05)

		recognizer.stop_continuous_recognition_async().get()

	def start(self):
		if self._thread is not None:
			return
		self._thread = threading.Thread(target=self._run, daemon=True)
		self._thread.start()

	def stop(self):
		self._started = False
		if self._thread is not None:
			self._thread.join(timeout=3)
			self._thread = None

	def results(self) -> Generator[ASRResult, None, None]:
		while True:
			res = self._q.get()
			yield res
