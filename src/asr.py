from typing import Optional, Tuple

from .config import AppConfig


class ASR:
	def __init__(self, config: AppConfig):
		import azure.cognitiveservices.speech as speechsdk
		self.speechsdk = speechsdk
		self.config = config
		speech_key = config.azure_speech_key
		region = config.azure_speech_region
		if not speech_key or not region:
			raise RuntimeError("Azure Speech key/region required for ASR")
		self.speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=region)
		self.speech_config.speech_recognition_language = config.default_source_lang
		self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
		self.recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, audio_config=self.audio_config)

	def transcribe(self, audio_pcm16: bytes, sample_rate: int) -> Tuple[str, Optional[str]]:
		# For compatibility with pipeline, do a one-shot recognition from mic
		result = self.recognizer.recognize_once_async().get()
		if result.reason == self.speechsdk.ResultReason.RecognizedSpeech:
			return result.text, self.config.default_source_lang
		return "", None
