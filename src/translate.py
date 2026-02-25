from typing import Optional

from .config import AppConfig


def translate_text(text: str, target_lang: str, config: AppConfig, source_lang: Optional[str] = None) -> str:
	if not text.strip():
		return text
	# Prefer DeepL if key exists
	if config.deepl_api_key:
		try:
			import deepl
			translator = deepl.Translator(config.deepl_api_key)
			result = translator.translate_text(text, target_lang=target_lang.upper())
			return result.text
		except Exception:
			pass
	# Fallback to deep-translator (Google Translate backend)
	try:
		from deep_translator import GoogleTranslator
		gt = GoogleTranslator(source="auto", target=target_lang)
		return gt.translate(text)
	except Exception:
		return text
