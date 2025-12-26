"""
Audio Generation Script
Generates audio files for all test cases using both Cartesia and Eleven Labs
"""

import json
import yaml
import time
import os
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from tqdm import tqdm
from dotenv import load_dotenv

from cartesia_client import CartesiaClient
from elevenlabs_client import ElevenLabsClient

# Load environment variables from .env file
load_dotenv()


class AudioGenerator:
    """Orchestrates audio generation for TTS evaluation"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the generator

        Args:
            config_path: Path to configuration file
        """
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        # Get API keys from config or environment variables
        cartesia_key = os.getenv("CARTESIA_API_KEY", self.config["api_keys"]["cartesia"])
        elevenlabs_key = os.getenv("ELEVENLABS_API_KEY", self.config["api_keys"]["elevenlabs"])

        # Initialize clients
        self.cartesia_client = CartesiaClient(
            api_key=cartesia_key,
            output_dir=self.config["output"]["cartesia_output_dir"]
        )

        self.elevenlabs_client = ElevenLabsClient(
            api_key=elevenlabs_key,
            output_dir=self.config["output"]["elevenlabs_output_dir"]
        )

        # Track generation metadata
        self.generation_log = []

    def load_test_cases(self, language: str = "en") -> List[Dict]:
        """
        Load test cases for a specific language

        Args:
            language: Language code (en, de, zh, ja)

        Returns:
            List of test cases
        """
        # Map language codes to filenames
        language_files = {
            "en": "english.json",
            "de": "german.json",
            "zh": "mandarin.json",
            "ja": "japanese.json"
        }

        filename = language_files.get(language, f"{language}.json")
        test_file = Path(f"test_cases/{filename}")

        if not test_file.exists():
            print(f"Warning: Test file {test_file} not found")
            return []

        with open(test_file) as f:
            data = json.load(f)

        # Flatten test cases from categories
        test_cases = []
        for category in data["test_categories"]:
            for test in category["tests"]:
                test["category"] = category["category"]
                test["language"] = language
                test_cases.append(test)

        return test_cases

    def generate_for_provider(
        self,
        provider: str,
        test_case: Dict,
        voice_id: str,
        skip_existing: bool = True
    ) -> Dict:
        """
        Generate audio for a single test case using specified provider

        Args:
            provider: "cartesia" or "elevenlabs"
            test_case: Test case dict
            voice_id: Voice ID to use
            skip_existing: Skip if output file already exists

        Returns:
            Result dict
        """
        test_id = test_case["test_id"]
        text = test_case["text"]
        language = test_case["language"]

        # Check if file already exists
        if skip_existing:
            output_dir = self.config["output"][f"{provider}_output_dir"]
            expected_file = Path(output_dir) / f"{provider}_{test_id}.mp3"
            if expected_file.exists():
                return {
                    "status": "skipped",
                    "test_id": test_id,
                    "provider": provider,
                    "category": test_case.get("category", "unknown"),
                    "reason": "file already exists",
                    "file_path": str(expected_file)
                }

        if provider == "cartesia":
            # Get model_id from config
            model_id = self.config["models"]["cartesia"]["model_id"]
            result = self.cartesia_client.generate_and_save(
                test_id=test_id,
                text=text,
                voice_id=voice_id,
                language=language,
                model_id=model_id
            )
        elif provider == "elevenlabs":
            # Get model_id from config
            model_id = self.config["models"]["elevenlabs"]["model_id"]
            result = self.elevenlabs_client.generate_and_save(
                test_id=test_id,
                text=text,
                voice_id=voice_id,
                model_id=model_id,
                language_code=language
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

        # Add metadata
        result["provider"] = provider
        result["test_id"] = test_id
        result["category"] = test_case.get("category", "unknown")
        result["timestamp"] = datetime.now().isoformat()

        return result

    def generate_all(
        self,
        languages: List[str] = None,
        providers: List[str] = None,
        test_filter: str = None,
        skip_existing: bool = True
    ) -> Dict:
        """
        Generate audio for all test cases

        Args:
            languages: List of language codes to process (default: from config)
            providers: List of providers to use (default: ["cartesia", "elevenlabs"])
            test_filter: Optional filter for test IDs (e.g., "E1-" for heteronyms only)

        Returns:
            Summary dict with generation results
        """
        if languages is None:
            languages = self.config["testing"]["current_focus"]

        if providers is None:
            providers = ["cartesia", "elevenlabs"]

        print(f"\n{'='*60}")
        print(f"TTS Audio Generation")
        print(f"{'='*60}")
        print(f"Languages: {', '.join(languages)}")
        print(f"Providers: {', '.join(providers)}")
        print(f"{'='*60}\n")

        results = {
            "cartesia": [],
            "elevenlabs": [],
            "summary": {
                "total_tests": 0,
                "successful": 0,
                "failed": 0,
                "skipped": 0,
                "start_time": datetime.now().isoformat()
            }
        }

        # Process each language
        for language in languages:
            test_cases = self.load_test_cases(language)

            if test_filter:
                test_cases = [t for t in test_cases if test_filter in t["test_id"]]

            if not test_cases:
                print(f"No test cases found for language: {language}")
                continue

            print(f"\nProcessing {len(test_cases)} test cases for {language.upper()}")

            # Get voice IDs for this language
            cartesia_voice = self.config["models"]["cartesia"]["language_voices"].get(language)
            elevenlabs_voice = self.config["models"]["elevenlabs"]["language_voices"].get(language)

            # Generate audio for each test case
            for test_case in tqdm(test_cases, desc=f"{language.upper()} tests"):
                results["summary"]["total_tests"] += 1

                # Generate for each provider
                for provider in providers:
                    voice_id = cartesia_voice if provider == "cartesia" else elevenlabs_voice

                    if not voice_id:
                        print(f"\nWarning: No voice ID configured for {provider}/{language}")
                        continue

                    try:
                        result = self.generate_for_provider(
                            provider=provider,
                            test_case=test_case,
                            voice_id=voice_id,
                            skip_existing=skip_existing
                        )

                        results[provider].append(result)

                        if result["status"] == "success":
                            results["summary"]["successful"] += 1
                        elif result["status"] == "skipped":
                            results["summary"]["skipped"] += 1
                        else:
                            results["summary"]["failed"] += 1
                            print(f"\n❌ Failed: {provider} - {test_case['test_id']}")
                            print(f"   Error: {result.get('error', 'Unknown')}")

                        # Rate limiting - small delay between requests
                        time.sleep(0.5)

                    except Exception as e:
                        print(f"\n❌ Exception: {provider} - {test_case['test_id']}: {e}")
                        results["summary"]["failed"] += 1

        # Finalize summary
        results["summary"]["end_time"] = datetime.now().isoformat()
        results["summary"]["success_rate"] = (
            results["summary"]["successful"] / (results["summary"]["total_tests"] * len(providers))
            if results["summary"]["total_tests"] > 0 else 0
        )

        # Save generation log
        self._save_generation_log(results)

        return results

    def _save_generation_log(self, results: Dict):
        """Save generation log to JSON file"""
        log_file = Path("results") / f"generation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✅ Generation log saved to: {log_file}")

    def print_summary(self, results: Dict):
        """Print generation summary"""
        summary = results["summary"]

        print(f"\n{'='*60}")
        print(f"Generation Summary")
        print(f"{'='*60}")
        print(f"Total test cases: {summary['total_tests']}")
        print(f"Successful generations: {summary['successful']}")
        print(f"Skipped (already exist): {summary.get('skipped', 0)}")
        print(f"Failed generations: {summary['failed']}")
        if summary['successful'] + summary.get('skipped', 0) > 0:
            print(f"Success rate: {summary['success_rate']*100:.1f}%")
        print(f"{'='*60}\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate TTS audio for evaluation")
    parser.add_argument(
        "--languages",
        nargs="+",
        default=None,
        help="Languages to process (e.g., en de zh)"
    )
    parser.add_argument(
        "--providers",
        nargs="+",
        choices=["cartesia", "elevenlabs"],
        default=None,
        help="Providers to use"
    )
    parser.add_argument(
        "--filter",
        type=str,
        default=None,
        help="Filter test cases by ID prefix (e.g., E1- for heteronyms only)"
    )
    parser.add_argument(
        "--no-skip-existing",
        action="store_true",
        help="Regenerate files even if they already exist"
    )

    args = parser.parse_args()

    # Generate audio
    generator = AudioGenerator()
    results = generator.generate_all(
        languages=args.languages,
        providers=args.providers,
        test_filter=args.filter,
        skip_existing=not args.no_skip_existing
    )

    # Print summary
    generator.print_summary(results)


if __name__ == "__main__":
    main()
