"""
Interactive Evaluation Interface
Web-based tool for manual TTS evaluation and comparison
"""

import json
import yaml
import gradio as gr
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class EvaluationInterface:
    """Interactive evaluation interface for TTS comparison"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the evaluation interface"""
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.test_cases = []
        self.current_index = 0
        self.evaluations = []
        self.evaluated_test_ids = set()  # Track which tests are done

        # Create results directory
        Path("results").mkdir(exist_ok=True)

        # Load existing evaluations
        self._load_existing_evaluations()

    def load_test_cases(self, language: str = "en") -> List[Dict]:
        """Load test cases for evaluation"""
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
            return []

        with open(test_file) as f:
            data = json.load(f)

        # Load generation logs to get latency data
        latency_data = self._load_latency_data()

        # Flatten test cases
        test_cases = []
        for category in data["test_categories"]:
            for test in category["tests"]:
                test["category"] = category["category"]
                test["language"] = language

                # Add audio file paths
                test["cartesia_audio"] = f"outputs/cartesia/cartesia_{test['test_id']}.mp3"
                test["elevenlabs_audio"] = f"outputs/elevenlabs/elevenlabs_{test['test_id']}.mp3"

                # Check if audio files exist
                test["has_cartesia"] = Path(test["cartesia_audio"]).exists()
                test["has_elevenlabs"] = Path(test["elevenlabs_audio"]).exists()

                # Add latency data
                test["cartesia_latency"] = latency_data.get("cartesia", {}).get(test["test_id"], None)
                test["elevenlabs_latency"] = latency_data.get("elevenlabs", {}).get(test["test_id"], None)

                if test["has_cartesia"] or test["has_elevenlabs"]:
                    test_cases.append(test)

        return test_cases

    def _load_latency_data(self) -> Dict:
        """Load latency data from generation logs"""
        latency_data = {"cartesia": {}, "elevenlabs": {}}

        # Find all generation logs
        log_files = sorted(Path("results").glob("generation_log_*.json"))

        for log_file in log_files:
            try:
                with open(log_file) as f:
                    data = json.load(f)

                # Extract latency for each provider
                for provider in ["cartesia", "elevenlabs"]:
                    for entry in data.get(provider, []):
                        test_id = entry.get("test_id")
                        gen_time = entry.get("generation_time")
                        if test_id and gen_time:
                            latency_data[provider][test_id] = gen_time
            except:
                continue

        return latency_data

    def _load_existing_evaluations(self):
        """Load existing evaluations from file"""
        eval_file = Path("results/evaluations.json")

        if eval_file.exists():
            try:
                with open(eval_file) as f:
                    self.evaluations = json.load(f)

                # Track which tests have been evaluated
                self.evaluated_test_ids = {e["test_id"] for e in self.evaluations}

                print(f"✅ Loaded {len(self.evaluations)} existing evaluations")
                print(f"   Already evaluated: {sorted(self.evaluated_test_ids)}")
            except Exception as e:
                print(f"⚠️  Could not load existing evaluations: {e}")
                self.evaluations = []
                self.evaluated_test_ids = set()

    def get_current_test(self) -> Optional[Dict]:
        """Get the current test case"""
        if 0 <= self.current_index < len(self.test_cases):
            return self.test_cases[self.current_index]
        return None

    def save_evaluation(
        self,
        test_id: str,
        text: str,
        category: str,
        cartesia_latency_display: str,  # Display string like "1.41s ✅"
        elevenlabs_latency_display: str,  # Display string like "0.44s ✅"
        # Cartesia scores
        cartesia_pronunciation: int,
        cartesia_prosody: int,
        cartesia_emotion: int,
        cartesia_naturalness: int,
        cartesia_consistency: int,
        cartesia_notes: str,
        # ElevenLabs scores
        elevenlabs_pronunciation: int,
        elevenlabs_prosody: int,
        elevenlabs_emotion: int,
        elevenlabs_naturalness: int,
        elevenlabs_consistency: int,
        elevenlabs_notes: str,
        # Overall comparison
        winner: str,
        comparison_notes: str
    ):
        """Save evaluation for current test case"""

        # Parse latency from display strings (e.g., "1.41s ✅" -> 1.41)
        def parse_latency(latency_str):
            if not latency_str or latency_str == "N/A":
                return None
            try:
                # Extract just the number part before 's'
                return float(latency_str.split('s')[0])
            except:
                return None

        cartesia_latency = parse_latency(cartesia_latency_display)
        elevenlabs_latency = parse_latency(elevenlabs_latency_display)

        evaluation = {
            "test_id": test_id,
            "text": text,
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "latency": {
                "cartesia": cartesia_latency,
                "elevenlabs": elevenlabs_latency,
                "faster": "cartesia" if (cartesia_latency or 999) < (elevenlabs_latency or 999) else "elevenlabs" if elevenlabs_latency else None
            },
            "cartesia": {
                "pronunciation_accuracy": cartesia_pronunciation,
                "prosody": cartesia_prosody,
                "emotional_appropriateness": cartesia_emotion,
                "naturalness": cartesia_naturalness,
                "consistency": cartesia_consistency,
                "average_score": (
                    cartesia_pronunciation + cartesia_prosody + cartesia_emotion +
                    cartesia_naturalness + cartesia_consistency
                ) / 5,
                "notes": cartesia_notes
            },
            "elevenlabs": {
                "pronunciation_accuracy": elevenlabs_pronunciation,
                "prosody": elevenlabs_prosody,
                "emotional_appropriateness": elevenlabs_emotion,
                "naturalness": elevenlabs_naturalness,
                "consistency": elevenlabs_consistency,
                "average_score": (
                    elevenlabs_pronunciation + elevenlabs_prosody + elevenlabs_emotion +
                    elevenlabs_naturalness + elevenlabs_consistency
                ) / 5,
                "notes": elevenlabs_notes
            },
            "comparison": {
                "winner": winner,
                "notes": comparison_notes
            }
        }

        # Check if this test was already evaluated (update vs new)
        existing_idx = None
        for i, e in enumerate(self.evaluations):
            if e["test_id"] == test_id:
                existing_idx = i
                break

        if existing_idx is not None:
            # Update existing evaluation
            self.evaluations[existing_idx] = evaluation
            self.evaluated_test_ids.add(test_id)
            self._save_evaluations()
            return f"✅ Updated evaluation for {test_id}"
        else:
            # New evaluation
            self.evaluations.append(evaluation)
            self.evaluated_test_ids.add(test_id)
            self._save_evaluations()
            return f"✅ Saved evaluation for {test_id}"

    def _save_evaluations(self):
        """Save evaluations to JSON file"""
        output_file = Path("results/evaluations.json")

        with open(output_file, 'w') as f:
            json.dump(self.evaluations, f, indent=2)

    def next_test(self):
        """Move to next test case"""
        self.current_index += 1
        if self.current_index >= len(self.test_cases):
            self.current_index = len(self.test_cases) - 1
        return self._update_display()

    def previous_test(self):
        """Move to previous test case"""
        self.current_index -= 1
        if self.current_index < 0:
            self.current_index = 0
        return self._update_display()

    def _get_test_choices(self):
        """Get formatted test choices for dropdown"""
        choices = []
        for i, test in enumerate(self.test_cases):
            test_id = test["test_id"]
            category = test["category"]
            status = "✅" if test_id in self.evaluated_test_ids else "⏳"
            # Format: "E1-H1 ✅ - heteronyms"
            choice = f"{test_id} {status} - {category}"
            choices.append(choice)
        return choices

    def jump_to_test(self, choice):
        """Jump to a specific test by dropdown selection"""
        if not choice:
            return self._update_display()

        # Extract test_id from choice (format: "E1-H1 ✅ - heteronyms")
        test_id = choice.split()[0]

        # Find index
        for i, test in enumerate(self.test_cases):
            if test["test_id"] == test_id:
                self.current_index = i
                break

        return self._update_display()

    def jump_to_unevaluated(self):
        """Jump to next unevaluated test case"""
        # Find first unevaluated test from current position
        start_idx = self.current_index
        for i in range(start_idx, len(self.test_cases)):
            if self.test_cases[i]["test_id"] not in self.evaluated_test_ids:
                self.current_index = i
                return self._update_display()

        # Wrap around - check from beginning
        for i in range(0, start_idx):
            if self.test_cases[i]["test_id"] not in self.evaluated_test_ids:
                self.current_index = i
                return self._update_display()

        # All evaluated - stay at current
        return self._update_display()

    def filter_by_category(self, category):
        """Update test selector choices based on category filter"""
        if category == "All":
            return gr.Dropdown(choices=self._get_test_choices())

        # Filter choices by category
        filtered_choices = []
        for i, test in enumerate(self.test_cases):
            if test["category"] == category:
                test_id = test["test_id"]
                status = "✅" if test_id in self.evaluated_test_ids else "⏳"
                choice = f"{test_id} {status} - {category}"
                filtered_choices.append(choice)

        return gr.Dropdown(choices=filtered_choices)

    def _get_existing_evaluation(self, test_id: str) -> Optional[Dict]:
        """Get existing evaluation for a test ID"""
        for evaluation in self.evaluations:
            if evaluation["test_id"] == test_id:
                return evaluation
        return None

    def _update_display(self):
        """Update the display with current test case"""
        test = self.get_current_test()

        if not test:
            # Return defaults for all fields (22 fields total)
            return ["No test cases loaded"] + [""] * 21

        # Show progress with evaluation status
        is_evaluated = test["test_id"] in self.evaluated_test_ids
        status = "✅ DONE" if is_evaluated else "⏳ TODO"
        progress = f"Test {self.current_index + 1}/{len(self.test_cases)} - {test['test_id']} [{status}]"

        # Format latency displays
        c_latency = test.get("cartesia_latency")
        e_latency = test.get("elevenlabs_latency")

        c_latency_str = f"{c_latency:.2f}s" if c_latency else "N/A"
        e_latency_str = f"{e_latency:.2f}s" if e_latency else "N/A"

        # Add speed comparison
        if c_latency and e_latency:
            diff = abs(c_latency - e_latency)
            faster = "Cartesia" if c_latency < e_latency else "Eleven Labs"
            speedup = max(c_latency, e_latency) / min(c_latency, e_latency)
            c_latency_str += f" {'✅' if c_latency < e_latency else '⏱️'}"
            e_latency_str += f" {'✅' if e_latency < c_latency else '⏱️'}"

        # Check if this test has been evaluated before
        existing_eval = self._get_existing_evaluation(test["test_id"]) if is_evaluated else None

        if existing_eval:
            # Load previous evaluation data
            cart = existing_eval["cartesia"]
            elev = existing_eval["elevenlabs"]
            comp = existing_eval["comparison"]

            return [
                progress,
                test["test_id"],
                test["text"],
                test["category"],
                test.get("expected_challenges", []),
                c_latency_str,
                e_latency_str,
                test["cartesia_audio"] if test["has_cartesia"] else None,
                test["elevenlabs_audio"] if test["has_elevenlabs"] else None,
                f"Category: {test['category']}\nImportance: {test.get('importance', 'N/A')}",
                # Cartesia scores (pre-filled from existing evaluation)
                cart["pronunciation_accuracy"],
                cart["prosody"],
                cart["emotional_appropriateness"],
                cart["naturalness"],
                cart["consistency"],
                cart.get("notes", ""),
                # Eleven Labs scores (pre-filled from existing evaluation)
                elev["pronunciation_accuracy"],
                elev["prosody"],
                elev["emotional_appropriateness"],
                elev["naturalness"],
                elev["consistency"],
                elev.get("notes", ""),
                # Comparison (pre-filled from existing evaluation)
                comp.get("winner", "Tie"),
                comp.get("notes", "")
            ]
        else:
            # Return defaults for new evaluation
            return [
                progress,
                test["test_id"],
                test["text"],
                test["category"],
                test.get("expected_challenges", []),
                c_latency_str,
                e_latency_str,
                test["cartesia_audio"] if test["has_cartesia"] else None,
                test["elevenlabs_audio"] if test["has_elevenlabs"] else None,
                f"Category: {test['category']}\nImportance: {test.get('importance', 'N/A')}",
                # Default scores (all 3s)
                3, 3, 3, 3, 3, "",  # Cartesia
                3, 3, 3, 3, 3, "",  # Eleven Labs
                "Tie", ""  # Comparison
            ]

    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface"""

        with gr.Blocks(title="TTS Evaluation Interface", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# TTS Evaluation: Cartesia vs Eleven Labs")
            gr.Markdown("Listen to both audio samples and rate them on each criterion (1-5 scale)")

            with gr.Row():
                progress_label = gr.Textbox(label="Progress", interactive=False)

            with gr.Row():
                test_id_display = gr.Textbox(label="Test ID", interactive=False)
                category_display = gr.Textbox(label="Category", interactive=False)

            with gr.Row():
                text_display = gr.Textbox(label="Text", lines=3, interactive=False)

            with gr.Row():
                metadata_display = gr.Textbox(label="Test Metadata", lines=2, interactive=False)

            with gr.Row():
                cartesia_latency_display = gr.Textbox(label="Cartesia Latency", interactive=False, value="N/A")
                elevenlabs_latency_display = gr.Textbox(label="Eleven Labs Latency", interactive=False, value="N/A")

            gr.Markdown("## Audio Samples")

            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Cartesia Sonic 3")
                    cartesia_audio = gr.Audio(label="Cartesia", type="filepath")

                with gr.Column():
                    gr.Markdown("### Eleven Labs Flash v2.5")
                    elevenlabs_audio = gr.Audio(label="Eleven Labs", type="filepath")

            gr.Markdown("## Evaluation Scores (1-5)")

            # Add evaluation guide
            with gr.Accordion("📖 Evaluation Guide (Click to expand)", open=False):
                gr.Markdown("""
### Rating Criteria Explained

| Criterion | What to Listen For | Good (4-5) | Poor (1-2) |
|-----------|-------------------|------------|-----------|
| **Pronunciation** | Are words said correctly? Heteronyms, foreign words, technical terms | All words clear and correct | Mispronunciations, wrong stress on syllables |
| **Prosody** | The "melody" of speech: pitch patterns, timing, emphasis | Natural rhythm, appropriate pauses, emphasis on right words | Monotone, robotic cadence, wrong word stress |
| **Emotion** | Does the tone match the content? | Appropriate energy/affect for the text | Flat when should be excited, upbeat when should be serious |
| **Naturalness** | Overall human-ness: voice quality, artifacts | Sounds like a real person, warm voice, no glitches | Robotic quality, buzzy/tinny, clicks, unnatural breaths |
| **Consistency** | Same quality throughout | Stable voice quality, no sudden changes | Voice breaks, quality drops, speed inconsistencies |

### Prosody vs Naturalness (Key Difference!)

- **Prosody** = The melody/rhythm (pitch, timing, stress patterns)
- **Naturalness** = Overall "does this sound human?" (voice quality, warmth, artifacts)

*Example:* A voice can have perfect rhythm/emphasis (good prosody) but still sound robotic (poor naturalness), or vice versa.

### Quick Tips:
- Listen multiple times - first for pronunciation, then for feel
- Compare directly: play both back-to-back
- Note specific moments: "0:03 - weird pause", "breath at 0:15"
- Trust your gut: if something sounds off, it probably is
                """)

            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Cartesia Scores")
                    cartesia_pronunciation = gr.Slider(1, 5, step=1, label="1️⃣ Pronunciation Accuracy", value=3, info="Are words pronounced correctly? (heteronyms, technical terms)")
                    cartesia_prosody = gr.Slider(1, 5, step=1, label="2️⃣ Prosody (Melody/Rhythm)", value=3, info="Natural pitch, timing, emphasis? (not monotone/robotic)")
                    cartesia_emotion = gr.Slider(1, 5, step=1, label="3️⃣ Emotional Appropriateness", value=3, info="Does tone match content? (energy, affect)")
                    cartesia_naturalness = gr.Slider(1, 5, step=1, label="4️⃣ Naturalness (Human-ness)", value=3, info="Sounds like real person? (no artifacts/glitches)")
                    cartesia_consistency = gr.Slider(1, 5, step=1, label="5️⃣ Consistency", value=3, info="Stable quality throughout? (no breaks/drops)")
                    cartesia_notes = gr.Textbox(label="Notes", lines=3, placeholder="Specific observations: timestamps, issues, strengths...")

                with gr.Column():
                    gr.Markdown("### Eleven Labs Scores")
                    elevenlabs_pronunciation = gr.Slider(1, 5, step=1, label="1️⃣ Pronunciation Accuracy", value=3, info="Are words pronounced correctly? (heteronyms, technical terms)")
                    elevenlabs_prosody = gr.Slider(1, 5, step=1, label="2️⃣ Prosody (Melody/Rhythm)", value=3, info="Natural pitch, timing, emphasis? (not monotone/robotic)")
                    elevenlabs_emotion = gr.Slider(1, 5, step=1, label="3️⃣ Emotional Appropriateness", value=3, info="Does tone match content? (energy, affect)")
                    elevenlabs_naturalness = gr.Slider(1, 5, step=1, label="4️⃣ Naturalness (Human-ness)", value=3, info="Sounds like real person? (no artifacts/glitches)")
                    elevenlabs_consistency = gr.Slider(1, 5, step=1, label="5️⃣ Consistency", value=3, info="Stable quality throughout? (no breaks/drops)")
                    elevenlabs_notes = gr.Textbox(label="Notes", lines=3, placeholder="Specific observations: timestamps, issues, strengths...")

            gr.Markdown("## Overall Comparison")

            with gr.Row():
                winner = gr.Radio(
                    choices=["Cartesia", "Eleven Labs", "Tie"],
                    label="Which was better overall?",
                    value="Tie"
                )

            comparison_notes = gr.Textbox(
                label="Comparison Notes",
                lines=3,
                placeholder="Key differences, which aspects made one better, etc."
            )

            with gr.Row():
                save_button = gr.Button("💾 Save Evaluation", variant="primary")
                save_status = gr.Textbox(label="Status", interactive=False)

            with gr.Row():
                prev_button = gr.Button("⬅️ Previous")
                next_button = gr.Button("Next ➡️")

            # Quick navigation
            with gr.Row():
                with gr.Column():
                    test_selector = gr.Dropdown(
                        choices=self._get_test_choices(),
                        label="Jump to Test",
                        interactive=True
                    )
                with gr.Column():
                    category_filter = gr.Dropdown(
                        choices=["All"] + sorted(list(set(t["category"] for t in self.test_cases))),
                        value="All",
                        label="Filter by Category",
                        interactive=True
                    )
                with gr.Column():
                    jump_unevaluated_btn = gr.Button("⏭️ Jump to Next Unevaluated")

            # Event handlers
            def save_and_next(*args):
                """Save current evaluation and move to next"""
                status = self.save_evaluation(*args)
                self.next_test()
                # Get updated display values (already includes all scores)
                display_values = list(self._update_display())
                # Return status + display values (no extra defaults needed)
                return [status] + display_values

            save_button.click(
                fn=save_and_next,
                inputs=[
                    test_id_display, text_display, category_display,
                    cartesia_latency_display, elevenlabs_latency_display,
                    cartesia_pronunciation, cartesia_prosody, cartesia_emotion,
                    cartesia_naturalness, cartesia_consistency, cartesia_notes,
                    elevenlabs_pronunciation, elevenlabs_prosody, elevenlabs_emotion,
                    elevenlabs_naturalness, elevenlabs_consistency, elevenlabs_notes,
                    winner, comparison_notes
                ],
                outputs=[
                    save_status, progress_label, test_id_display, text_display,
                    category_display, metadata_display,
                    cartesia_latency_display, elevenlabs_latency_display,
                    cartesia_audio, elevenlabs_audio, metadata_display,
                    cartesia_pronunciation, cartesia_prosody, cartesia_emotion,
                    cartesia_naturalness, cartesia_consistency, cartesia_notes,
                    elevenlabs_pronunciation, elevenlabs_prosody, elevenlabs_emotion,
                    elevenlabs_naturalness, elevenlabs_consistency, elevenlabs_notes,
                    winner, comparison_notes
                ]
            )

            prev_button.click(
                fn=self.previous_test,
                outputs=[
                    progress_label, test_id_display, text_display,
                    category_display, metadata_display,
                    cartesia_latency_display, elevenlabs_latency_display,
                    cartesia_audio, elevenlabs_audio, metadata_display,
                    # Also update scores when navigating
                    cartesia_pronunciation, cartesia_prosody, cartesia_emotion,
                    cartesia_naturalness, cartesia_consistency, cartesia_notes,
                    elevenlabs_pronunciation, elevenlabs_prosody, elevenlabs_emotion,
                    elevenlabs_naturalness, elevenlabs_consistency, elevenlabs_notes,
                    winner, comparison_notes
                ]
            )

            next_button.click(
                fn=self.next_test,
                outputs=[
                    progress_label, test_id_display, text_display,
                    category_display, metadata_display,
                    cartesia_latency_display, elevenlabs_latency_display,
                    cartesia_audio, elevenlabs_audio, metadata_display,
                    # Also update scores when navigating
                    cartesia_pronunciation, cartesia_prosody, cartesia_emotion,
                    cartesia_naturalness, cartesia_consistency, cartesia_notes,
                    elevenlabs_pronunciation, elevenlabs_prosody, elevenlabs_emotion,
                    elevenlabs_naturalness, elevenlabs_consistency, elevenlabs_notes,
                    winner, comparison_notes
                ]
            )

            # Test selector event handler
            test_selector.change(
                fn=self.jump_to_test,
                inputs=[test_selector],
                outputs=[
                    progress_label, test_id_display, text_display,
                    category_display, metadata_display,
                    cartesia_latency_display, elevenlabs_latency_display,
                    cartesia_audio, elevenlabs_audio, metadata_display,
                    cartesia_pronunciation, cartesia_prosody, cartesia_emotion,
                    cartesia_naturalness, cartesia_consistency, cartesia_notes,
                    elevenlabs_pronunciation, elevenlabs_prosody, elevenlabs_emotion,
                    elevenlabs_naturalness, elevenlabs_consistency, elevenlabs_notes,
                    winner, comparison_notes
                ]
            )

            # Category filter event handler
            category_filter.change(
                fn=self.filter_by_category,
                inputs=[category_filter],
                outputs=[test_selector]
            )

            # Jump to unevaluated button
            jump_unevaluated_btn.click(
                fn=self.jump_to_unevaluated,
                outputs=[
                    progress_label, test_id_display, text_display,
                    category_display, metadata_display,
                    cartesia_latency_display, elevenlabs_latency_display,
                    cartesia_audio, elevenlabs_audio, metadata_display,
                    cartesia_pronunciation, cartesia_prosody, cartesia_emotion,
                    cartesia_naturalness, cartesia_consistency, cartesia_notes,
                    elevenlabs_pronunciation, elevenlabs_prosody, elevenlabs_emotion,
                    elevenlabs_naturalness, elevenlabs_consistency, elevenlabs_notes,
                    winner, comparison_notes
                ]
            )

            # Initial load
            interface.load(
                fn=self._update_display,
                outputs=[
                    progress_label, test_id_display, text_display,
                    category_display, metadata_display,
                    cartesia_latency_display, elevenlabs_latency_display,
                    cartesia_audio, elevenlabs_audio, metadata_display,
                    # Load scores on initial load
                    cartesia_pronunciation, cartesia_prosody, cartesia_emotion,
                    cartesia_naturalness, cartesia_consistency, cartesia_notes,
                    elevenlabs_pronunciation, elevenlabs_prosody, elevenlabs_emotion,
                    elevenlabs_naturalness, elevenlabs_consistency, elevenlabs_notes,
                    winner, comparison_notes
                ]
            )

        return interface

    def launch(self, language: str = "en", share: bool = False):
        """Launch the evaluation interface"""
        print("Loading test cases...")
        self.test_cases = self.load_test_cases(language)

        if not self.test_cases:
            print(f"⚠️  No test cases with generated audio found for {language}")
            print("Please run generate_audio.py first to create audio files.")
            return

        print(f"✅ Loaded {len(self.test_cases)} test cases with audio files")

        # Jump to first unevaluated test
        if self.evaluated_test_ids:
            num_evaluated = len(self.evaluated_test_ids)
            num_remaining = len(self.test_cases) - num_evaluated
            print(f"📊 Progress: {num_evaluated} evaluated, {num_remaining} remaining")

            # Find first unevaluated test
            for i, test in enumerate(self.test_cases):
                if test["test_id"] not in self.evaluated_test_ids:
                    self.current_index = i
                    print(f"🎯 Starting at first unevaluated test: {test['test_id']}")
                    break
            else:
                print(f"🎉 All tests evaluated! Starting from beginning for review.")
                self.current_index = 0

        interface = self.create_interface()
        interface.launch(share=share)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Launch TTS evaluation interface")
    parser.add_argument(
        "--language",
        type=str,
        default="en",
        help="Language to evaluate (default: en)"
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a public share link"
    )

    args = parser.parse_args()

    evaluator = EvaluationInterface()
    evaluator.launch(language=args.language, share=args.share)


if __name__ == "__main__":
    main()
