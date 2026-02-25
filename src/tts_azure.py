from typing import Optional
import os

from .config import AppConfig


AZURE_VOICE_MAP = {
	("female", "us"): "en-US-JennyNeural",
	("female", "uk"): "en-GB-SoniaNeural",
	("female", "au"): "en-AU-NatashaNeural",
	("female", "gr"): "el-GR-AthinaNeural",
	("male", "us"): "en-US-GuyNeural",
	("male", "uk"): "en-GB-RyanNeural",
	("male", "au"): "en-AU-WilliamNeural",
	("male", "gr"): "el-GR-NestorasNeural",
}

# Native style presets per accent/gender
NATIVE_PRESETS = {
	("female", "us"): {"rate": "+4%", "pitch": "+2%", "style": "newscast-casual"},
	("male", "us"): {"rate": "+2%", "pitch": "0%", "style": "newscast"},
	("female", "uk"): {"rate": "0%", "pitch": "-2%", "style": "narration-professional"},
	("male", "uk"): {"rate": "-2%", "pitch": "-4%", "style": "narration-relaxed"},
	("female", "au"): {"rate": "+2%", "pitch": "+1%", "style": "chat"},
	("male", "au"): {"rate": "+1%", "pitch": "0%", "style": "chat"},
	("female", "gr"): {"rate": "0%", "pitch": "-1%", "style": "general"},
	("male", "gr"): {"rate": "0%", "pitch": "-2%", "style": "general"},
}


def tts_azure(text: str, config: AppConfig, voice: Optional[str] = None, accent: Optional[str] = None, native_style: bool = False):
	key = config.azure_speech_key or os.getenv("AZURE_SPEECH_KEY")
	region = config.azure_speech_region or os.getenv("AZURE_SPEECH_REGION")
	if not key or not region:
		raise RuntimeError("Missing Azure speech key/region")
	try:
		import azure.cognitiveservices.speech as speechsdk
		speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
		gender = voice or config.default_voice
		acc = accent or config.default_accent
		voice_name = AZURE_VOICE_MAP.get((gender, acc), AZURE_VOICE_MAP.get(("female", "us")))
		audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
		synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

		if native_style:
			preset = NATIVE_PRESETS.get((gender, acc), {"rate": "0%", "pitch": "0%", "style": "general"})
			ssml = f"""
				<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='https://www.w3.org/2001/mstts' xml:lang='en-US'>
					<voice name='{voice_name}'>
						<mstts:express-as style='{preset["style"]}'>
							<prosody rate='{preset["rate"]}' pitch='{preset["pitch"]}'>
								{text}
							</prosody>
						</mstts:express-as>
					</voice>
				</speak>
			"""
			result = synthesizer.speak_ssml_async(ssml).get()
		else:
			speech_config.speech_synthesis_voice_name = voice_name
			result = synthesizer.speak_text_async(text).get()

		if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
			raise RuntimeError(f"Azure TTS failed: {result.reason}")
	except Exception as e:
		raise RuntimeError(f"Azure TTS failed: {e}")
