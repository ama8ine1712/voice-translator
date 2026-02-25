# Voice Translator (MVP)

[![Stars](https://img.shields.io/github/stars/ama8ine1712/voice-translator?style=flat&color=70a5fd)](https://github.com/ama8ine1712/voice-translator/stargazers)
[![Issues](https://img.shields.io/github/issues/ama8ine1712/voice-translator?style=flat&color=ff7b72)](https://github.com/ama8ine1712/voice-translator/issues)
![Theme](https://img.shields.io/badge/theme-tokyonight-1a1b27?style=flat)

An efficient speech-to-speech translator that can switch accents and gender using neural TTS. Pipeline: Mic audio → VAD segmentation → ASR (Whisper) → Translation → TTS (ElevenLabs/Azure).

## Setup (Windows)

1. Install Python 3.10+.
2. (Recommended) Install FFmpeg and add to PATH if using pydub.
3. Create and activate venv:
   - PowerShell:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
5. Copy `.env.example` to `.env` and fill keys.

## API Keys
- ELEVENLABS_API_KEY: for ElevenLabs TTS
- AZURE_SPEECH_KEY, AZURE_SPEECH_REGION: for Azure TTS
- DEEPL_API_KEY: for DeepL translation (optional if using Google)

## Run (CLI)
```powershell
python main.py --target-lang es --voice female --accent us
```

## Notes
- For best naturalness, use ElevenLabs or Azure neural voices.
- You can run without TTS keys to just see transcripts/translations.
