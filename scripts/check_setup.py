"""
Setup Validation Script
Checks if everything is configured correctly before running evaluations
"""

import sys
import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def check_config_file():
    """Check if config.yaml exists and is valid"""
    print("\n1. Checking config.yaml...")

    config_file = Path("config.yaml")
    if not config_file.exists():
        print("   ❌ config.yaml not found")
        return False

    try:
        with open(config_file) as f:
            config = yaml.safe_load(f)
        print("   ✅ config.yaml found and valid")
        return config
    except Exception as e:
        print(f"   ❌ Error reading config.yaml: {e}")
        return False


def check_api_keys(config):
    """Check if API keys are configured"""
    print("\n2. Checking API keys...")

    issues = []

    # Check for .env file
    env_file = Path(".env")
    if env_file.exists():
        print("   ✅ .env file found")
    else:
        print("   ⚠️  No .env file (you can create one from .env.example)")

    # Check Cartesia key (from env or config)
    cartesia_key = os.getenv("CARTESIA_API_KEY", config.get("api_keys", {}).get("cartesia", ""))
    cartesia_source = "env" if os.getenv("CARTESIA_API_KEY") else "config"

    if not cartesia_key or cartesia_key == "YOUR_CARTESIA_API_KEY" or cartesia_key == "CARTESIA_API_KEY":
        issues.append("   ❌ Cartesia API key not configured")
    else:
        print(f"   ✅ Cartesia API key configured ({cartesia_key[:10]}... from {cartesia_source})")

    # Check Eleven Labs key (from env or config)
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY", config.get("api_keys", {}).get("elevenlabs", ""))
    elevenlabs_source = "env" if os.getenv("ELEVENLABS_API_KEY") else "config"

    if not elevenlabs_key or elevenlabs_key == "YOUR_ELEVENLABS_API_KEY" or elevenlabs_key == "ELEVENLABS_API_KEY":
        issues.append("   ❌ Eleven Labs API key not configured")
    else:
        print(f"   ✅ Eleven Labs API key configured ({elevenlabs_key[:10]}... from {elevenlabs_source})")

    if issues:
        for issue in issues:
            print(issue)
        print("\n   💡 Option 1: Create .env file and add keys there")
        print("   💡 Option 2: Edit config.yaml and add your API keys")
        return False

    return True


def check_voice_ids(config):
    """Check if voice IDs are configured"""
    print("\n3. Checking voice IDs...")

    issues = []

    # Check Cartesia voice
    cartesia_voice = config.get("models", {}).get("cartesia", {}).get("language_voices", {}).get("en")
    if not cartesia_voice:
        issues.append("   ⚠️  Cartesia English voice ID not configured")
    else:
        print(f"   ✅ Cartesia English voice configured ({cartesia_voice[:20]}...)")

    # Check Eleven Labs voice
    elevenlabs_voice = config.get("models", {}).get("elevenlabs", {}).get("language_voices", {}).get("en")
    if not elevenlabs_voice:
        issues.append("   ⚠️  Eleven Labs English voice ID not configured")
    else:
        print(f"   ✅ Eleven Labs English voice configured ({elevenlabs_voice[:20]}...)")

    if issues:
        for issue in issues:
            print(issue)
        print("\n   💡 See SETUP_GUIDE.md for instructions on finding voice IDs")
        return False

    return True


def check_test_cases():
    """Check if test cases exist"""
    print("\n4. Checking test cases...")

    test_file = Path("test_cases/english.json")
    if not test_file.exists():
        print("   ❌ test_cases/english.json not found")
        return False

    import json
    try:
        with open(test_file) as f:
            data = json.load(f)

        total_tests = sum(len(cat["tests"]) for cat in data.get("test_categories", []))
        print(f"   ✅ Found {total_tests} English test cases")
        return True

    except Exception as e:
        print(f"   ❌ Error reading test cases: {e}")
        return False


def check_directories():
    """Check if required directories exist"""
    print("\n5. Checking directories...")

    dirs = ["outputs/cartesia", "outputs/elevenlabs", "results", "scripts"]
    all_exist = True

    for dir_path in dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"   ✅ {dir_path}/")
        else:
            print(f"   ❌ {dir_path}/ not found")
            all_exist = False

    return all_exist


def check_dependencies():
    """Check if required Python packages are installed"""
    print("\n6. Checking Python dependencies...")

    required = {
        "yaml": "pyyaml",
        "requests": "requests",
        "gradio": "gradio",
        "tqdm": "tqdm"
    }

    missing = []
    for module, package in required.items():
        try:
            __import__(module)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} not installed")
            missing.append(package)

    if missing:
        print(f"\n   💡 Install missing packages: pip install {' '.join(missing)}")
        return False

    return True


def check_audio_files():
    """Check if any audio files have been generated"""
    print("\n7. Checking for generated audio...")

    cartesia_files = list(Path("outputs/cartesia").glob("*.mp3"))
    elevenlabs_files = list(Path("outputs/elevenlabs").glob("*.mp3"))

    if cartesia_files:
        print(f"   ✅ Found {len(cartesia_files)} Cartesia audio files")
    else:
        print("   ⚠️  No Cartesia audio files found")

    if elevenlabs_files:
        print(f"   ✅ Found {len(elevenlabs_files)} Eleven Labs audio files")
    else:
        print("   ⚠️  No Eleven Labs audio files found")

    if not cartesia_files and not elevenlabs_files:
        print("\n   💡 Run: python scripts/generate_audio.py --filter E1-H1")
        print("      This will test audio generation with a single test case")

    return True  # Not critical for initial setup


def main():
    """Run all checks"""
    print("="*60)
    print("TTS Evaluation Framework - Setup Check")
    print("="*60)

    checks = []

    # Run checks
    config = check_config_file()
    checks.append(("config", bool(config)))

    if config:
        checks.append(("api_keys", check_api_keys(config)))
        checks.append(("voice_ids", check_voice_ids(config)))

    checks.append(("test_cases", check_test_cases()))
    checks.append(("directories", check_directories()))
    checks.append(("dependencies", check_dependencies()))
    check_audio_files()  # Informational only

    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)

    passed = sum(1 for _, status in checks if status)
    total = len(checks)

    for name, status in checks:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {name.replace('_', ' ').title()}")

    print("="*60)

    if passed == total:
        print("\n🎉 All checks passed! You're ready to go.")
        print("\nNext steps:")
        print("1. Generate test audio: python scripts/generate_audio.py --filter E1-H1")
        print("2. Launch evaluation: python scripts/evaluate.py --language en")
        return 0
    else:
        print(f"\n⚠️  {total - passed} check(s) failed. Please fix the issues above.")
        print("\nSee SETUP_GUIDE.md for detailed setup instructions.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
