"""
Performance Analysis: Quality ratings comparison
Analyzes TTS quality across providers, categories, and criteria
"""

import json
from pathlib import Path
from collections import defaultdict
import statistics
from typing import Dict, List


class PerformanceAnalyzer:
    """Analyze TTS quality performance"""

    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        self.evaluations = []

        # Criteria names
        self.criteria = [
            "pronunciation_accuracy",
            "prosody",
            "emotional_appropriateness",
            "naturalness",
            "consistency"
        ]

        self.criteria_labels = {
            "pronunciation_accuracy": "Pronunciation",
            "prosody": "Prosody",
            "emotional_appropriateness": "Emotion",
            "naturalness": "Naturalness",
            "consistency": "Consistency"
        }

    def load_data(self):
        """Load evaluations"""
        eval_file = self.results_dir / "evaluations.json"
        if eval_file.exists():
            with open(eval_file) as f:
                self.evaluations = json.load(f)

        print(f"✅ Loaded {len(self.evaluations)} evaluations")

    def overall_comparison(self):
        """Overall performance comparison"""
        print("\n" + "="*70)
        print("OVERALL PERFORMANCE COMPARISON")
        print("="*70)

        cart_scores = []
        elev_scores = []

        for eval_item in self.evaluations:
            cart_scores.append(eval_item["cartesia"]["average_score"])
            elev_scores.append(eval_item["elevenlabs"]["average_score"])

        cart_avg = statistics.mean(cart_scores)
        elev_avg = statistics.mean(elev_scores)

        print(f"\n📊 Average Quality Scores (1-5 scale, n={len(self.evaluations)}):")
        print(f"   Cartesia Sonic 3:      {cart_avg:.2f} ± {statistics.stdev(cart_scores):.2f}")
        print(f"   ElevenLabs Flash v2.5: {elev_avg:.2f} ± {statistics.stdev(elev_scores):.2f}")

        diff = cart_avg - elev_avg
        if abs(diff) < 0.05:
            print(f"\n   → Essentially tied")
        else:
            better = "Cartesia" if diff > 0 else "ElevenLabs"
            print(f"\n   → {better} scores {abs(diff):.2f} points higher ({abs(diff)/5*100:.1f}% better)")

        # Win/Loss/Tie breakdown
        wins = {"Cartesia": 0, "Eleven Labs": 0, "Tie": 0}
        for eval_item in self.evaluations:
            winner = eval_item["comparison"]["winner"]
            wins[winner] += 1

        total = sum(wins.values())
        print(f"\n🏆 Head-to-Head Results:")
        print(f"   Cartesia wins:   {wins['Cartesia']:2d} ({wins['Cartesia']/total*100:.1f}%)")
        print(f"   ElevenLabs wins: {wins['Eleven Labs']:2d} ({wins['Eleven Labs']/total*100:.1f}%)")
        print(f"   Ties:            {wins['Tie']:2d} ({wins['Tie']/total*100:.1f}%)")

    def criteria_breakdown(self):
        """Break down by individual criteria"""
        print("\n" + "="*70)
        print("PERFORMANCE BY CRITERIA")
        print("="*70)

        print("\n📊 Average scores by criterion (1-5 scale):\n")
        print(f"{'Criterion':<20} {'Cartesia':>10} {'ElevenLabs':>12} {'Difference':>12} {'Winner':>10}")
        print("-" * 70)

        for criterion in self.criteria:
            cart_scores = [e["cartesia"][criterion] for e in self.evaluations]
            elev_scores = [e["elevenlabs"][criterion] for e in self.evaluations]

            cart_avg = statistics.mean(cart_scores)
            elev_avg = statistics.mean(elev_scores)
            diff = cart_avg - elev_avg

            winner = "Cartesia" if diff > 0.1 else ("ElevenLabs" if diff < -0.1 else "Tie")
            diff_str = f"{diff:+.2f}"

            label = self.criteria_labels[criterion]
            print(f"{label:<20} {cart_avg:>10.2f} {elev_avg:>12.2f} {diff_str:>12} {winner:>10}")

        print("\n🎯 Key insights:")

        # Find strengths/weaknesses
        for criterion in self.criteria:
            cart_scores = [e["cartesia"][criterion] for e in self.evaluations]
            elev_scores = [e["elevenlabs"][criterion] for e in self.evaluations]

            cart_avg = statistics.mean(cart_scores)
            elev_avg = statistics.mean(elev_scores)
            diff = cart_avg - elev_avg

            label = self.criteria_labels[criterion]

            if diff > 0.15:
                print(f"   • Cartesia is stronger in {label} (+{diff:.2f})")
            elif diff < -0.15:
                print(f"   • ElevenLabs is stronger in {label} ({diff:.2f})")

    def category_breakdown(self):
        """Break down by test category"""
        print("\n" + "="*70)
        print("PERFORMANCE BY CATEGORY")
        print("="*70)

        # Group by category
        by_category = defaultdict(lambda: {"cartesia": [], "elevenlabs": [], "wins": {"Cartesia": 0, "Eleven Labs": 0, "Tie": 0}})

        for eval_item in self.evaluations:
            category = eval_item["category"]
            by_category[category]["cartesia"].append(eval_item["cartesia"]["average_score"])
            by_category[category]["elevenlabs"].append(eval_item["elevenlabs"]["average_score"])
            by_category[category]["wins"][eval_item["comparison"]["winner"]] += 1

        print("\n📊 Average scores by category:\n")
        print(f"{'Category':<25} {'Cartesia':>10} {'ElevenLabs':>12} {'Δ':>8} {'Winner':>12}")
        print("-" * 70)

        for category in sorted(by_category.keys()):
            data = by_category[category]
            cart_avg = statistics.mean(data["cartesia"])
            elev_avg = statistics.mean(data["elevenlabs"])
            diff = cart_avg - elev_avg

            # Determine winner based on head-to-head
            wins = data["wins"]
            if wins["Cartesia"] > wins["Eleven Labs"]:
                winner = "Cartesia"
            elif wins["Eleven Labs"] > wins["Cartesia"]:
                winner = "ElevenLabs"
            else:
                winner = "Tie"

            diff_str = f"{diff:+.2f}"
            print(f"{category:<25} {cart_avg:>10.2f} {elev_avg:>12.2f} {diff_str:>8} {winner:>12}")

            # Show win breakdown
            total = sum(wins.values())
            print(f"{'':25} ({wins['Cartesia']}W-{wins['Eleven Labs']}L-{wins['Tie']}T)")

    def english_deep_dive(self):
        """Deep dive into English performance"""
        print("\n" + "="*70)
        print("ENGLISH DEEP DIVE")
        print("="*70)

        # Filter English evaluations
        english_evals = [e for e in self.evaluations if e["test_id"].startswith("E")]

        if not english_evals:
            print("\n⚠️  No English evaluations found")
            return

        print(f"\n📊 English evaluations: {len(english_evals)} test cases")

        # Overall English scores
        cart_scores = [e["cartesia"]["average_score"] for e in english_evals]
        elev_scores = [e["elevenlabs"]["average_score"] for e in english_evals]

        print(f"\n🎯 Overall English Performance:")
        print(f"   Cartesia:   {statistics.mean(cart_scores):.2f} ± {statistics.stdev(cart_scores):.2f}")
        print(f"   ElevenLabs: {statistics.mean(elev_scores):.2f} ± {statistics.stdev(elev_scores):.2f}")

        # Win/Loss breakdown for English
        wins = {"Cartesia": 0, "Eleven Labs": 0, "Tie": 0}
        for eval_item in english_evals:
            wins[eval_item["comparison"]["winner"]] += 1

        total = len(english_evals)
        print(f"\n   Head-to-head: {wins['Cartesia']}W - {wins['Eleven Labs']}L - {wins['Tie']}T")
        print(f"   Cartesia win rate: {wins['Cartesia']/total*100:.1f}%")

        # Break down by English category
        print("\n" + "-"*70)
        print("ENGLISH CATEGORIES BREAKDOWN")
        print("-"*70)

        by_category = defaultdict(list)
        for eval_item in english_evals:
            by_category[eval_item["category"]].append(eval_item)

        for category in sorted(by_category.keys()):
            evals = by_category[category]
            print(f"\n📌 {category.replace('_', ' ').title()} ({len(evals)} tests):")

            cart_avg = statistics.mean([e["cartesia"]["average_score"] for e in evals])
            elev_avg = statistics.mean([e["elevenlabs"]["average_score"] for e in evals])

            print(f"   Cartesia:   {cart_avg:.2f}")
            print(f"   ElevenLabs: {elev_avg:.2f}")

            # Win breakdown
            cat_wins = {"Cartesia": 0, "Eleven Labs": 0, "Tie": 0}
            for e in evals:
                cat_wins[e["comparison"]["winner"]] += 1

            print(f"   Results: {cat_wins['Cartesia']}W - {cat_wins['Eleven Labs']}L - {cat_wins['Tie']}T")

            # Show specific issues
            issues = []
            for e in evals:
                if e["cartesia"]["average_score"] < 3:
                    issues.append(f"      • {e['test_id']}: Cartesia struggled (score: {e['cartesia']['average_score']:.1f})")
                if e["elevenlabs"]["average_score"] < 3:
                    issues.append(f"      • {e['test_id']}: ElevenLabs struggled (score: {e['elevenlabs']['average_score']:.1f})")

            if issues:
                print(f"   Issues:")
                for issue in issues:
                    print(issue)

        # Criteria breakdown for English
        print("\n" + "-"*70)
        print("ENGLISH CRITERIA BREAKDOWN")
        print("-"*70)

        print(f"\n{'Criterion':<20} {'Cartesia':>10} {'ElevenLabs':>12} {'Δ':>8}")
        print("-" * 55)

        for criterion in self.criteria:
            cart_scores = [e["cartesia"][criterion] for e in english_evals]
            elev_scores = [e["elevenlabs"][criterion] for e in english_evals]

            cart_avg = statistics.mean(cart_scores)
            elev_avg = statistics.mean(elev_scores)
            diff = cart_avg - elev_avg

            label = self.criteria_labels[criterion]
            diff_str = f"{diff:+.2f}"
            print(f"{label:<20} {cart_avg:>10.2f} {elev_avg:>12.2f} {diff_str:>8}")

        # Find standout tests
        print("\n" + "-"*70)
        print("ENGLISH STANDOUT CASES")
        print("-"*70)

        print("\n🌟 Cartesia's best performances (relative advantage):")
        cart_best = sorted(english_evals,
                          key=lambda e: e["cartesia"]["average_score"] - e["elevenlabs"]["average_score"],
                          reverse=True)[:5]

        for e in cart_best:
            diff = e["cartesia"]["average_score"] - e["elevenlabs"]["average_score"]
            if diff > 0:
                print(f"   {e['test_id']:8} (+{diff:.1f}): {e['category']:20} - {e['text'][:50]}...")
                if e["comparison"].get("notes"):
                    print(f"            Note: {e['comparison']['notes'][:80]}")

        print("\n🌟 ElevenLabs' best performances (relative advantage):")
        elev_best = sorted(english_evals,
                          key=lambda e: e["elevenlabs"]["average_score"] - e["cartesia"]["average_score"],
                          reverse=True)[:5]

        for e in elev_best:
            diff = e["elevenlabs"]["average_score"] - e["cartesia"]["average_score"]
            if diff > 0:
                print(f"   {e['test_id']:8} (+{diff:.1f}): {e['category']:20} - {e['text'][:50]}...")
                if e["comparison"].get("notes"):
                    print(f"            Note: {e['comparison']['notes'][:80]}")

        # Biggest quality gaps
        print("\n⚠️  Biggest disagreements (largest score differences):")
        disagreements = sorted(english_evals,
                              key=lambda e: abs(e["cartesia"]["average_score"] - e["elevenlabs"]["average_score"]),
                              reverse=True)[:5]

        for e in disagreements:
            cart_score = e["cartesia"]["average_score"]
            elev_score = e["elevenlabs"]["average_score"]
            diff = cart_score - elev_score
            winner = "Cartesia" if diff > 0 else "ElevenLabs"
            print(f"   {e['test_id']:8} {winner:11} by {abs(diff):.1f}: {e['category']:20}")
            print(f"            Cartesia: {cart_score:.1f}, ElevenLabs: {elev_score:.1f}")
            print(f"            Text: {e['text'][:70]}...")

    def strengths_weaknesses(self):
        """Identify specific strengths and weaknesses"""
        print("\n" + "="*70)
        print("STRENGTHS & WEAKNESSES ANALYSIS")
        print("="*70)

        # Find tests where each provider scored poorly (< 3)
        cart_weak = []
        elev_weak = []

        for e in self.evaluations:
            if e["cartesia"]["average_score"] < 3:
                cart_weak.append(e)
            if e["elevenlabs"]["average_score"] < 3:
                elev_weak.append(e)

        print(f"\n⚠️  Cartesia weaknesses ({len(cart_weak)} tests scored < 3.0):")
        if cart_weak:
            # Group by category
            by_cat = defaultdict(list)
            for e in cart_weak:
                by_cat[e["category"]].append(e)

            for cat, evals in sorted(by_cat.items()):
                print(f"\n   {cat} ({len(evals)} tests):")
                for e in sorted(evals, key=lambda x: x["cartesia"]["average_score"]):
                    score = e["cartesia"]["average_score"]
                    print(f"      {e['test_id']:8} (score: {score:.1f}): {e['text'][:60]}...")
                    if e["cartesia"].get("notes"):
                        print(f"               Note: {e['cartesia']['notes'][:70]}")
        else:
            print("   None! All tests scored ≥ 3.0")

        print(f"\n⚠️  ElevenLabs weaknesses ({len(elev_weak)} tests scored < 3.0):")
        if elev_weak:
            # Group by category
            by_cat = defaultdict(list)
            for e in elev_weak:
                by_cat[e["category"]].append(e)

            for cat, evals in sorted(by_cat.items()):
                print(f"\n   {cat} ({len(evals)} tests):")
                for e in sorted(evals, key=lambda x: x["elevenlabs"]["average_score"]):
                    score = e["elevenlabs"]["average_score"]
                    print(f"      {e['test_id']:8} (score: {score:.1f}): {e['text'][:60]}...")
                    if e["elevenlabs"].get("notes"):
                        print(f"               Note: {e['elevenlabs']['notes'][:70]}")
        else:
            print("   None! All tests scored ≥ 3.0")

    def executive_summary(self):
        """Generate executive summary"""
        print("\n" + "="*70)
        print("EXECUTIVE SUMMARY")
        print("="*70)

        # Overall scores
        cart_scores = [e["cartesia"]["average_score"] for e in self.evaluations]
        elev_scores = [e["elevenlabs"]["average_score"] for e in self.evaluations]

        cart_avg = statistics.mean(cart_scores)
        elev_avg = statistics.mean(elev_scores)

        # Win/Loss
        wins = {"Cartesia": 0, "Eleven Labs": 0, "Tie": 0}
        for e in self.evaluations:
            wins[e["comparison"]["winner"]] += 1

        print("\n🎯 Key Findings:")
        print()

        # 1. Overall winner
        if cart_avg > elev_avg + 0.1:
            print(f"1. 🏆 Cartesia Sonic 3 is the overall quality winner")
            print(f"   - Cartesia: {cart_avg:.2f}/5.0")
            print(f"   - ElevenLabs: {elev_avg:.2f}/5.0")
            print(f"   - Advantage: +{cart_avg - elev_avg:.2f} points")
        elif elev_avg > cart_avg + 0.1:
            print(f"1. 🏆 ElevenLabs Flash v2.5 is the overall quality winner")
            print(f"   - ElevenLabs: {elev_avg:.2f}/5.0")
            print(f"   - Cartesia: {cart_avg:.2f}/5.0")
            print(f"   - Advantage: +{elev_avg - cart_avg:.2f} points")
        else:
            print(f"1. ⚖️  Quality is essentially tied")
            print(f"   - Cartesia: {cart_avg:.2f}/5.0")
            print(f"   - ElevenLabs: {elev_avg:.2f}/5.0")

        print()
        print(f"2. 📊 Head-to-head record: {wins['Cartesia']}W - {wins['Eleven Labs']}L - {wins['Tie']}T")

        total = sum(wins.values())
        if wins['Cartesia'] > wins['Eleven Labs']:
            print(f"   - Cartesia wins {wins['Cartesia']/total*100:.0f}% of matchups")
        elif wins['Eleven Labs'] > wins['Cartesia']:
            print(f"   - ElevenLabs wins {wins['Eleven Labs']/total*100:.0f}% of matchups")

        print()

        # 3. Strengths
        print("3. 💪 Relative strengths:")
        for criterion in self.criteria:
            cart_scores_c = [e["cartesia"][criterion] for e in self.evaluations]
            elev_scores_c = [e["elevenlabs"][criterion] for e in self.evaluations]

            cart_avg_c = statistics.mean(cart_scores_c)
            elev_avg_c = statistics.mean(elev_scores_c)
            diff = cart_avg_c - elev_avg_c

            label = self.criteria_labels[criterion]

            if abs(diff) > 0.1:
                stronger = "Cartesia" if diff > 0 else "ElevenLabs"
                print(f"   - {stronger:11} stronger in {label:15} ({diff:+.2f})")

    def run_analysis(self):
        """Run complete performance analysis"""
        print("\n" + "="*70)
        print("PERFORMANCE ANALYSIS: Quality Ratings Comparison")
        print("="*70)

        self.load_data()

        if not self.evaluations:
            print("\n⚠️  No evaluations found. Please complete evaluations first.")
            return

        self.overall_comparison()
        self.criteria_breakdown()
        self.category_breakdown()
        self.english_deep_dive()
        self.strengths_weaknesses()
        self.executive_summary()


def main():
    analyzer = PerformanceAnalyzer()
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
