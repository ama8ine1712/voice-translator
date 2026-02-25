import os
import azure.cognitiveservices.speech as speechsdk

def create_speech_config(config):
    # Try to get key & region from config or environment
    speech_key = getattr(config, "azure_speech_key", None) or os.getenv("AZURE_SPEECH_KEY")
    speech_region = getattr(config, "azure_speech_region", None) or os.getenv("AZURE_SPEECH_REGION")

    # Handle missing credentials gracefully
    if not speech_key or not speech_region:
        print("⚠️ Azure Speech key or region not set.")
        print("   Please set them in your code or as environment variables:")
        print("   AZURE_SPEECH_KEY=<your_key>")
        print("   AZURE_SPEECH_REGION=<your_region>\n")
        return None  # prevent crash

    try:
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        print("✅ SpeechConfig created successfully.")
        return speech_config
    except Exception as e:
        print(f"❌ Failed to create SpeechConfig: {e}")
        return None





