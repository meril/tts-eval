"""
Cartesia TTS API Client
Generates audio using Cartesia Sonic 3 model
"""

import os
import time
from pathlib import Path
from typing import Dict, Optional
import requests


class CartesiaClient:
    """Client for Cartesia TTS API (Sonic 3)"""

    def __init__(self, api_key: str, output_dir: str = "outputs/cartesia"):
        """
        Initialize Cartesia client

        Args:
            api_key: Cartesia API key
            output_dir: Directory to save generated audio files
        """
        self.api_key = api_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "https://api.cartesia.ai"

    def generate_speech(
        self,
        text: str,
        voice_id: str,
        model_id: str = "sonic-3",  # Updated to sonic-3
        output_format: str = "mp3",
        language: str = "en"
    ) -> Dict:
        """
        Generate speech from text using Cartesia API

        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use
            model_id: Model ID (default: "sonic-3")
            output_format: Output format (mp3, wav, etc.)
            language: Language code

        Returns:
            Dict with status, file_path, and metadata
        """
        headers = {
            "X-API-Key": self.api_key,
            "Cartesia-Version": "2025-04-16",  # Updated to latest API version
            "Content-Type": "application/json"
        }

        payload = {
            "model_id": model_id,
            "transcript": text,
            "voice": {
                "mode": "id",
                "id": voice_id
            },
            "output_format": {
                "container": output_format,
                "encoding": "pcm_f32le" if output_format == "wav" else "mp3",
                "sample_rate": 44100  # Higher quality sample rate
            },
            "language": language,
            "speed": "normal",
            "generation_config": {
                "speed": 1.0,
                "volume": 1.0
            }
        }

        start_time = time.time()

        try:
            # Use streaming to measure TTFB accurately
            response = requests.post(
                f"{self.base_url}/tts/bytes",
                headers=headers,
                json=payload,
                timeout=30,
                stream=True
            )

            response.raise_for_status()

            # Read first chunk to get accurate TTFB
            chunks = []
            for chunk in response.iter_content(chunk_size=8192):
                if chunks == []:
                    # First chunk received - this is TTFB
                    ttfb = time.time() - start_time
                chunks.append(chunk)

            audio_data = b''.join(chunks)
            total_time = time.time() - start_time

            return {
                "status": "success",
                "audio_data": audio_data,
                "ttfb": ttfb,
                "total_time": total_time,
                "generation_time": ttfb,  # Keep for backwards compatibility
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
        language: str = "en",
        model_id: str = "sonic-english"
    ) -> Dict:
        """
        Generate speech and save to file

        Args:
            test_id: Test case ID
            text: Text to convert
            voice_id: Voice ID
            language: Language code
            model_id: Model ID

        Returns:
            Dict with result information
        """
        result = self.generate_speech(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            language=language
        )

        if result["status"] == "success":
            filename = f"cartesia_{test_id}.mp3"
            file_path = self.save_audio(result["audio_data"], filename)
            result["file_path"] = file_path
            del result["audio_data"]  # Remove binary data from result

        return result


if __name__ == "__main__":
    # Test the client
    import yaml

    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    api_key = config["api_keys"]["cartesia"]
    if api_key == "YOUR_CARTESIA_API_KEY":
        print("Please set your Cartesia API key in config.yaml")
    else:
        client = CartesiaClient(api_key)

        # Test generation
        result = client.generate_and_save(
            test_id="test",
            text="This is a test of the Cartesia text to speech system.",
            voice_id=config["models"]["cartesia"]["language_voices"]["en"],
            language="en"
        )

        print(f"Result: {result}")
