"""
Latency Analysis: Cartesia Sonic vs ElevenLabs Flash v2.5
Analyzes generation latency distributions and correlations with quality
"""

import json
from pathlib import Path
from collections import defaultdict
import statistics
from typing import Dict, List, Tuple


class LatencyAnalyzer:
    """Analyze TTS generation latency"""

    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        self.generation_logs = []
        self.evaluations = []
        self.latency_data = {"cartesia": [], "elevenlabs": []}
        self.latency_by_language = defaultdict(lambda: {"cartesia": [], "elevenlabs": []})

    def load_data(self):
        """Load generation logs and evaluations"""
        # Load all generation logs
        log_files = sorted(self.results_dir.glob("generation_log_*.json"))
        for log_file in log_files:
            with open(log_file) as f:
                self.generation_logs.append(json.load(f))

        # Load evaluations
        eval_file = self.results_dir / "evaluations.json"
        if eval_file.exists():
            with open(eval_file) as f:
                self.evaluations = json.load(f)

        print(f"✅ Loaded {len(self.generation_logs)} generation logs")
        print(f"✅ Loaded {len(self.evaluations)} evaluations")

    def extract_latency_data(self):
        """Extract latency from generation logs"""
        for log in self.generation_logs:
            for provider in ["cartesia", "elevenlabs"]:
                if provider in log:
                    for entry in log[provider]:
                        if entry["status"] == "success" and "generation_time" in entry:
                            latency = entry["generation_time"]
                            self.latency_data[provider].append(latency)

                            # Get language from test_id or category
                            test_id = entry.get("test_id", "")
                            if test_id.startswith("E"):
                                language = "en"
                            elif test_id.startswith("D"):
                                language = "de"
                            elif test_id.startswith("C"):
                                language = "zh"
                            elif test_id.startswith("J"):
                                language = "ja"
                            else:
                                language = "unknown"

                            self.latency_by_language[language][provider].append(latency)

        print(f"\n📊 Latency data points:")
        print(f"   Cartesia: {len(self.latency_data['cartesia'])}")
        print(f"   ElevenLabs: {len(self.latency_data['elevenlabs'])}")

    def compute_statistics(self, values: List[float]) -> Dict:
        """Compute statistical measures"""
        if not values:
            return {}

        return {
            "count": len(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "stdev": statistics.stdev(values) if len(values) > 1 else 0,
            "min": min(values),
            "max": max(values),
            "p25": statistics.quantiles(values, n=4)[0] if len(values) >= 4 else None,
            "p75": statistics.quantiles(values, n=4)[2] if len(values) >= 4 else None,
        }

    def compare_latency(self):
        """Compare latency between providers"""
        print("\n" + "="*70)
        print("OVERALL LATENCY COMPARISON")
        print("="*70)

        cart_stats = self.compute_statistics(self.latency_data["cartesia"])
        elev_stats = self.compute_statistics(self.latency_data["elevenlabs"])

        print("\n📈 Cartesia Sonic 3:")
        print(f"   Count:      {cart_stats['count']}")
        print(f"   Mean:       {cart_stats['mean']:.3f}s")
        print(f"   Median:     {cart_stats['median']:.3f}s")
        print(f"   Std Dev:    {cart_stats['stdev']:.3f}s")
        print(f"   Min:        {cart_stats['min']:.3f}s")
        print(f"   Max:        {cart_stats['max']:.3f}s")
        if cart_stats['p25']:
            print(f"   25th %ile:  {cart_stats['p25']:.3f}s")
            print(f"   75th %ile:  {cart_stats['p75']:.3f}s")

        print("\n📈 ElevenLabs Flash v2.5:")
        print(f"   Count:      {elev_stats['count']}")
        print(f"   Mean:       {elev_stats['mean']:.3f}s")
        print(f"   Median:     {elev_stats['median']:.3f}s")
        print(f"   Std Dev:    {elev_stats['stdev']:.3f}s")
        print(f"   Min:        {elev_stats['min']:.3f}s")
        print(f"   Max:        {elev_stats['max']:.3f}s")
        if elev_stats['p25']:
            print(f"   25th %ile:  {elev_stats['p25']:.3f}s")
            print(f"   75th %ile:  {elev_stats['p75']:.3f}s")

        # Calculate speedup
        if cart_stats['mean'] and elev_stats['mean']:
            speedup = cart_stats['mean'] / elev_stats['mean']
            faster = "ElevenLabs" if speedup > 1 else "Cartesia"
            speedup_pct = abs(speedup - 1) * 100

            print("\n🏆 Winner:")
            print(f"   {faster} is {speedup_pct:.1f}% faster on average")
            print(f"   Speedup ratio: {speedup:.2f}x")

            # Median comparison
            median_speedup = cart_stats['median'] / elev_stats['median']
            print(f"\n   Median speedup: {median_speedup:.2f}x")

            # Consistency comparison
            cart_cv = cart_stats['stdev'] / cart_stats['mean']  # Coefficient of variation
            elev_cv = elev_stats['stdev'] / elev_stats['mean']
            more_consistent = "Cartesia" if cart_cv < elev_cv else "ElevenLabs"
            print(f"\n📊 Consistency (lower is better):")
            print(f"   Cartesia CV:    {cart_cv:.3f}")
            print(f"   ElevenLabs CV:  {elev_cv:.3f}")
            print(f"   {more_consistent} is more consistent")

    def analyze_by_language(self):
        """Analyze latency by language"""
        print("\n" + "="*70)
        print("LATENCY BY LANGUAGE")
        print("="*70)

        language_names = {
            "en": "English",
            "de": "German",
            "zh": "Mandarin",
            "ja": "Japanese"
        }

        for lang_code in ["en", "de", "zh", "ja"]:
            if lang_code not in self.latency_by_language:
                continue

            lang_name = language_names.get(lang_code, lang_code)
            print(f"\n🌍 {lang_name} ({lang_code}):")

            cart_latencies = self.latency_by_language[lang_code]["cartesia"]
            elev_latencies = self.latency_by_language[lang_code]["elevenlabs"]

            if cart_latencies:
                cart_stats = self.compute_statistics(cart_latencies)
                print(f"   Cartesia:   {cart_stats['mean']:.3f}s (±{cart_stats['stdev']:.3f}s) n={cart_stats['count']}")
            else:
                print(f"   Cartesia:   No data")

            if elev_latencies:
                elev_stats = self.compute_statistics(elev_latencies)
                print(f"   ElevenLabs: {elev_stats['mean']:.3f}s (±{elev_stats['stdev']:.3f}s) n={elev_stats['count']}")
            else:
                print(f"   ElevenLabs: No data")

            # Compare
            if cart_latencies and elev_latencies:
                speedup = cart_stats['mean'] / elev_stats['mean']
                faster = "ElevenLabs" if speedup > 1 else "Cartesia"
                speedup_pct = abs(speedup - 1) * 100
                print(f"   → {faster} is {speedup_pct:.1f}% faster ({speedup:.2f}x)")

    def correlate_latency_quality(self):
        """Analyze correlation between latency and quality scores"""
        print("\n" + "="*70)
        print("LATENCY vs QUALITY CORRELATION")
        print("="*70)

        if not self.evaluations:
            print("\n⚠️  No evaluations available for correlation analysis")
            return

        # Extract latency and quality data
        cart_data = []  # (latency, quality_score)
        elev_data = []

        for eval_item in self.evaluations:
            test_id = eval_item["test_id"]

            # Get latency (convert to float if string)
            cart_latency = eval_item.get("latency", {}).get("cartesia")
            elev_latency = eval_item.get("latency", {}).get("elevenlabs")

            # Convert to float if needed
            if cart_latency is not None:
                try:
                    cart_latency = float(cart_latency)
                except (ValueError, TypeError):
                    cart_latency = None

            if elev_latency is not None:
                try:
                    elev_latency = float(elev_latency)
                except (ValueError, TypeError):
                    elev_latency = None

            # Get quality scores
            cart_quality = eval_item.get("cartesia", {}).get("average_score")
            elev_quality = eval_item.get("elevenlabs", {}).get("average_score")

            if cart_latency and cart_quality:
                cart_data.append((cart_latency, cart_quality))
            if elev_latency and elev_quality:
                elev_data.append((elev_latency, elev_quality))

        print(f"\n📊 Data points for correlation:")
        print(f"   Cartesia:   {len(cart_data)} evaluations")
        print(f"   ElevenLabs: {len(elev_data)} evaluations")

        # Compute correlation
        def pearson_correlation(data: List[Tuple[float, float]]) -> float:
            if len(data) < 2:
                return 0.0

            x_values = [x for x, y in data]
            y_values = [y for x, y in data]

            n = len(data)
            mean_x = statistics.mean(x_values)
            mean_y = statistics.mean(y_values)

            numerator = sum((x - mean_x) * (y - mean_y) for x, y in data)
            denominator_x = sum((x - mean_x) ** 2 for x in x_values)
            denominator_y = sum((y - mean_y) ** 2 for y in y_values)

            if denominator_x == 0 or denominator_y == 0:
                return 0.0

            return numerator / (denominator_x * denominator_y) ** 0.5

        if cart_data:
            cart_corr = pearson_correlation(cart_data)
            print(f"\n🔗 Cartesia - Latency vs Quality correlation: {cart_corr:.3f}")
            if abs(cart_corr) < 0.3:
                print(f"   → Weak correlation (latency doesn't strongly affect quality)")
            elif abs(cart_corr) < 0.7:
                print(f"   → Moderate correlation")
            else:
                print(f"   → Strong correlation")

        if elev_data:
            elev_corr = pearson_correlation(elev_data)
            print(f"\n🔗 ElevenLabs - Latency vs Quality correlation: {elev_corr:.3f}")
            if abs(elev_corr) < 0.3:
                print(f"   → Weak correlation (latency doesn't strongly affect quality)")
            elif abs(elev_corr) < 0.7:
                print(f"   → Moderate correlation")
            else:
                print(f"   → Strong correlation")

        # Quality comparison
        if cart_data and elev_data:
            cart_avg_quality = statistics.mean([q for l, q in cart_data])
            elev_avg_quality = statistics.mean([q for l, q in elev_data])

            print(f"\n📊 Average Quality Scores (1-5 scale):")
            print(f"   Cartesia:   {cart_avg_quality:.2f}")
            print(f"   ElevenLabs: {elev_avg_quality:.2f}")

            quality_diff = cart_avg_quality - elev_avg_quality
            if abs(quality_diff) < 0.1:
                print(f"   → Essentially tied")
            else:
                better = "Cartesia" if quality_diff > 0 else "ElevenLabs"
                print(f"   → {better} scores {abs(quality_diff):.2f} points higher")

    def generate_summary(self):
        """Generate executive summary"""
        print("\n" + "="*70)
        print("EXECUTIVE SUMMARY")
        print("="*70)

        cart_stats = self.compute_statistics(self.latency_data["cartesia"])
        elev_stats = self.compute_statistics(self.latency_data["elevenlabs"])

        if cart_stats and elev_stats:
            speedup = cart_stats['mean'] / elev_stats['mean']

            print("\n🎯 Key Findings:")
            print()

            if speedup > 1.1:
                print(f"1. ⚡ ElevenLabs Flash v2.5 is {(speedup-1)*100:.1f}% FASTER than Cartesia Sonic 3")
                print(f"   - ElevenLabs: {elev_stats['mean']:.3f}s average")
                print(f"   - Cartesia:   {cart_stats['mean']:.3f}s average")
            elif speedup < 0.9:
                print(f"1. ⚡ Cartesia Sonic 3 is {(1/speedup-1)*100:.1f}% FASTER than ElevenLabs Flash v2.5")
                print(f"   - Cartesia:   {cart_stats['mean']:.3f}s average")
                print(f"   - ElevenLabs: {elev_stats['mean']:.3f}s average")
            else:
                print(f"1. ⚖️  Both providers have similar latency")
                print(f"   - Cartesia:   {cart_stats['mean']:.3f}s average")
                print(f"   - ElevenLabs: {elev_stats['mean']:.3f}s average")

            print()

            # Consistency
            cart_cv = cart_stats['stdev'] / cart_stats['mean']
            elev_cv = elev_stats['stdev'] / elev_stats['mean']
            if cart_cv < elev_cv * 0.9:
                print(f"2. 📊 Cartesia is MORE CONSISTENT (CV: {cart_cv:.3f} vs {elev_cv:.3f})")
            elif elev_cv < cart_cv * 0.9:
                print(f"2. 📊 ElevenLabs is MORE CONSISTENT (CV: {elev_cv:.3f} vs {cart_cv:.3f})")
            else:
                print(f"2. 📊 Both providers have similar consistency")

            print()

            # Language differences
            print("3. 🌍 Language-specific performance:")
            for lang in ["en", "de", "zh", "ja"]:
                if lang in self.latency_by_language:
                    cart_lang = self.latency_by_language[lang]["cartesia"]
                    elev_lang = self.latency_by_language[lang]["elevenlabs"]
                    if cart_lang and elev_lang:
                        lang_speedup = statistics.mean(cart_lang) / statistics.mean(elev_lang)
                        faster = "ElevenLabs" if lang_speedup > 1 else "Cartesia"
                        print(f"   - {lang.upper()}: {faster} is faster ({lang_speedup:.2f}x)")

    def run_analysis(self):
        """Run complete analysis"""
        print("\n" + "="*70)
        print("LATENCY ANALYSIS: Cartesia Sonic vs ElevenLabs Flash v2.5")
        print("="*70)

        self.load_data()
        self.extract_latency_data()
        self.compare_latency()
        self.analyze_by_language()
        self.correlate_latency_quality()
        self.generate_summary()


def main():
    analyzer = LatencyAnalyzer()
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
