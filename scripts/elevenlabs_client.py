"""
Eleven Labs TTS API Client
Generates audio using Eleven Labs Flash v2.5 model
"""

import os
import time
from pathlib import Path
from typing import Dict, Optional
import requests


class ElevenLabsClient:
    """Client for Eleven Labs TTS API (Flash v2.5)"""

    def __init__(self, api_key: str, output_dir: str = "outputs/elevenlabs"):
        """
        Initialize Eleven Labs client

        Args:
            api_key: Eleven Labs API key
            output_dir: Directory to save generated audio files
        """
        self.api_key = api_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "https://api.elevenlabs.io/v1"

    def generate_speech(
        self,
        text: str,
        voice_id: str,
        model_id: str = "eleven_flash_v2_5",
        output_format: str = "mp3_44100_128",
        language_code: Optional[str] = None
    ) -> Dict:
        """
        Generate speech from text using Eleven Labs API

        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use
            model_id: Model ID (default: "eleven_flash_v2_5")
            output_format: Output format
            language_code: Optional ISO 639-1 language code (e.g., 'ja' for Japanese)

        Returns:
            Dict with status, file_path, and metadata
        """
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }

        # Add language-specific parameters
        if language_code:
            payload["language_code"] = language_code
            # For Japanese, enable text normalization (improves pronunciation but increases latency)
            if language_code == "ja":
                payload["apply_text_normalization"] = "on"

        start_time = time.time()

        try:
            response = requests.post(
                f"{self.base_url}/text-to-speech/{voice_id}",
                headers=headers,
                json=payload,
                params={"output_format": output_format},
                timeout=30
            )

            response.raise_for_status()

            generation_time = time.time() - start_time
            audio_data = response.content

            return {
                "status": "success",
                "audio_data": audio_data,
                "generation_time": generation_time,
                "text_length": len(text),
                "model_id": model_id,
                "voice_id": voice_id
            }

        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": str(e),
                "generation_time": time.time() - start_time
            }

    def save_audio(self, audio_data: bytes, filename: str) -> str:
        """
        Save audio data to file

        Args:
            audio_data: Audio bytes
            filename: Output filename

        Returns:
            Full path to saved file
        """
        file_path = self.output_dir / filename
        with open(file_path, 'wb') as f:
            f.write(audio_data)
        return str(file_path)

    def generate_and_save(
        self,
        test_id: str,
        text: str,
        voice_id: str,
        model_id: str = "eleven_flash_v2_5",
        language_code: Optional[str] = None
    ) -> Dict:
        """
        Generate speech and save to file

        Args:
            test_id: Test case ID
            text: Text to convert
            voice_id: Voice ID
            model_id: Model ID
            language_code: Optional ISO 639-1 language code

        Returns:
            Dict with result information
        """
        result = self.generate_speech(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            language_code=language_code
        )

        if result["status"] == "success":
            filename = f"elevenlabs_{test_id}.mp3"
            file_path = self.save_audio(result["audio_data"], filename)
            result["file_path"] = file_path
            del result["audio_data"]  # Remove binary data from result

        return result

    def list_voices(self) -> Dict:
        """
        List available voices

        Returns:
            Dict with available voices
        """
        headers = {
            "xi-api-key": self.api_key
        }

        try:
            response = requests.get(
                f"{self.base_url}/voices",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": str(e)
            }


if __name__ == "__main__":
    # Test the client
    import yaml

    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    api_key = config["api_keys"]["elevenlabs"]
    if api_key == "YOUR_ELEVENLABS_API_KEY":
        print("Please set your Eleven Labs API key in config.yaml")
    else:
        client = ElevenLabsClient(api_key)

        # List available voices
        voices = client.list_voices()
        print(f"Available voices: {voices}")

        # Test generation (if voice ID is configured)
        voice_id = config["models"]["elevenlabs"]["language_voices"]["en"]
        if voice_id:
            result = client.generate_and_save(
                test_id="test",
                text="This is a test of the Eleven Labs text to speech system.",
                voice_id=voice_id
            )
            print(f"Result: {result}")
