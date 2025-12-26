"""
Test Cartesia API with different configurations
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_cartesia(model_id, voice_id, text="Hello, this is a test of the Cartesia text to speech system."):
    """Test Cartesia API with specific configuration"""

    api_key = os.getenv("CARTESIA_API_KEY")

    print(f"\n{'='*60}")
    print(f"Testing: {model_id}")
    print(f"Voice: {voice_id}")
    print(f"Text: {text}")
    print(f"{'='*60}")

    headers = {
        "X-API-Key": api_key,
        "Cartesia-Version": "2024-06-10",
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
            "container": "mp3",
            "encoding": "mp3",
            "sample_rate": 44100  # Try higher sample rate
        }
    }

    try:
        print("Sending request...")
        response = requests.post(
            "https://api.cartesia.ai/tts/bytes",
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            filename = f"outputs/cartesia/test_{model_id.replace('-', '_')}.mp3"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ Success! Saved to: {filename}")
            print(f"File size: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


if __name__ == "__main__":
    # Get voice ID from config
    import yaml
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    voice_id = config["models"]["cartesia"]["language_voices"]["en"]

    print("\n🔍 Testing different Cartesia model configurations...")

    # Test different model IDs
    models_to_test = [
        "sonic-english",
        "sonic-multilingual",
        "sonic",
    ]

    for model in models_to_test:
        test_cartesia(model, voice_id)
        print()

    print("\n💡 Listen to the test files and see which sounds best!")
    print("   Files are in: outputs/cartesia/test_*.mp3")
