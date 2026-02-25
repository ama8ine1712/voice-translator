import argparse
from rich import print
from dotenv import load_dotenv

load_dotenv()

from src.config import AppConfig
from src.asr_whisper import WhisperASR
from src.translate import translate_text
from src.tts_elevenlabs import tts_elevenlabs
from src.tts_azure import tts_azure
from src.tts_queue import TTSQueue


def main():
	parser = argparse.ArgumentParser(description="Voice Translator")
	parser.add_argument("--target-lang", default=None, help="Target language code, e.g., es, fr, hi")
	parser.add_argument("--voice", default=None, choices=["male", "female"], help="Voice gender preference")
	parser.add_argument("--accent", default=None, choices=["us", "uk", "au", "gr"], help="Accent preference for English/Greek voices")
	parser.add_argument("--tts", default="auto", choices=["auto", "elevenlabs", "azure"], help="TTS provider")
	parser.add_argument("--native-style", action="store_true", help="Enable native accent profile with tuned pitch/pace/style")
	args = parser.parse_args()

	config = AppConfig()
	if args.target_lang:
		config.default_target_lang = args.target_lang
	if args.voice:
		config.default_voice = args.voice
	if args.accent:
		config.default_accent = args.accent

	print(f"[bold cyan]Starting[/bold cyan] -> target={config.default_target_lang}, voice={config.default_voice}, accent={config.default_accent}")

	# Decide TTS provider function
	provider = args.tts
	if provider == "auto":
		if config.elevenlabs_api_key:
			provider = "elevenlabs"
		elif config.azure_speech_key and config.azure_speech_region:
			provider = "azure"
		else:
			provider = "none"

	if provider == "elevenlabs":
		def speak_fn(text: str):
			tts_elevenlabs(text, config, voice=args.voice, accent=args.accent, native_style=args.native_style)
	elif provider == "azure":
		def speak_fn(text: str):
			tts_azure(text, config, voice=args.voice, accent=args.accent, native_style=args.native_style)
	else:
		def speak_fn(text: str):
			print(f"[red]No TTS provider configured. Text:[/red] {text}")

	ttsq = TTSQueue(speak_fn)
	ttsq.start()

	asr = WhisperASR(config)
	asr.start()
	print("[green]Streaming... Speak anytime. Press Ctrl+C to stop.[/green]")
	try:
		for res in asr.results():
			if not res.text:
				continue
			print(f"[yellow]{(res.language or '')}[/yellow] > {res.text}")
			translated = translate_text(res.text, config.default_target_lang, config, source_lang=res.language)
			print(f"[bold magenta]{config.default_target_lang}[/bold magenta] > {translated}")
			ttsq.enqueue(translated)
	except KeyboardInterrupt:
		print("\n[red]Stopping...[/red]")
	finally:
		asr.stop()
		ttsq.stop()


if __name__ == "__main__":
	main()
