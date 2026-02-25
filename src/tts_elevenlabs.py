from typing import Optional
import os

from .config import AppConfig
from .playback import play_wav_bytes


VOICE_MAP = {
	("female", "us"): "Rachel",
	("female", "uk"): "Bella",
	("female", "au"): "Charlotte",
	("female", "gr"): "Rachel",
	("male", "us"): "Adam",
	("male", "uk"): "Antoni",
	("male", "au"): "Daniel",
	("male", "gr"): "Adam",
}

NATIVE_PRESETS = {
	("female", "us"): {"stability": 0.3, "similarity_boost": 0.8, "style": 0.35},
	("male", "us"): {"stability": 0.35, "similarity_boost": 0.75, "style": 0.25},
	("female", "uk"): {"stability": 0.4, "similarity_boost": 0.8, "style": 0.2},
	("male", "uk"): {"stability": 0.45, "similarity_boost": 0.75, "style": 0.15},
	("female", "au"): {"stability": 0.35, "similarity_boost": 0.8, "style": 0.25},
	("male", "au"): {"stability": 0.4, "similarity_boost": 0.75, "style": 0.25},
	("female", "gr"): {"stability": 0.4, "similarity_boost": 0.8, "style": 0.2},
	("male", "gr"): {"stability": 0.45, "similarity_boost": 0.75, "style": 0.2},
}


def tts_elevenlabs(text: str, config: AppConfig, voice: Optional[str] = None, accent: Optional[str] = None, native_style: bool = False):
	api_key = config.elevenlabs_api_key or os.getenv("ELEVENLABS_API_KEY")
	if not api_key:
		raise RuntimeError("Missing ELEVENLABS_API_KEY")
	try:
		from elevenlabs import VoiceSettings, generate, set_api_key
		set_api_key(api_key)
		gender = voice or config.default_voice
		acc = accent or config.default_accent
		selected_name = VOICE_MAP.get((gender, acc), VOICE_MAP.get(("female", "us")))

		voice_settings = None
		if native_style:
			preset = NATIVE_PRESETS.get((gender, acc), {"stability": 0.4, "similarity_boost": 0.8, "style": 0.2})
			voice_settings = VoiceSettings(
				stability=preset["stability"],
				similarity_boost=preset["similarity_boost"],
				style=preset["style"],
			)
		audio = generate(
			text=text,
			voice=selected_name,
			model="eleven_multilingual_v2",
			voice_settings=voice_settings,
		)
		if isinstance(audio, bytes):
			play_wav_bytes(audio)
		else:
			buf = b"".join(chunk for chunk in audio)
			play_wav_bytes(buf)
	except Exception as e:
		raise RuntimeError(f"ElevenLabs TTS failed: {e}")
