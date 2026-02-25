import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class AppConfig:
	default_source_lang: str = os.getenv("DEFAULT_SOURCE_LANG", "en")
	default_target_lang: str = os.getenv("DEFAULT_TARGET_LANG", "es")
	default_voice: str = os.getenv("DEFAULT_VOICE", "female")
	default_accent: str = os.getenv("DEFAULT_ACCENT", "us")
	deepl_api_key: str | None = os.getenv("DEEPL_API_KEY")
	elevenlabs_api_key: str | None = os.getenv("ELEVENLABS_API_KEY")
	azure_speech_key: str | None = os.getenv("AZURE_SPEECH_KEY")
	azure_speech_region: str | None = os.getenv("AZURE_SPEECH_REGION")
	# ASR
	whisper_model_size: str = os.getenv("WHISPER_MODEL", "small")
	# Audio
	sample_rate: int = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
	frame_ms: int = int(os.getenv("VAD_FRAME_MS", "20"))
	aggressiveness: int = int(os.getenv("VAD_AGGRESSIVENESS", "2"))
	max_segment_ms: int = int(os.getenv("MAX_SEGMENT_MS", "8000"))
	padding_ms: int = int(os.getenv("VAD_PADDING_MS", "300"))
