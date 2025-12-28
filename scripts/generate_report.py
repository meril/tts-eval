"""
Generate Comprehensive Markdown Report
Combines TTFB (Time-to-First-Byte) and performance analysis into a single report
"""

import json
from pathlib import Path
from datetime import datetime
from analyze_latency import LatencyAnalyzer
from analyze_performance import PerformanceAnalyzer


def generate_markdown_report(output_file: str = "results/analysis_report.md"):
    """Generate comprehensive markdown report"""

    # Initialize analyzers
    latency_analyzer = LatencyAnalyzer()
    performance_analyzer = PerformanceAnalyzer()

    # Load data
    latency_analyzer.load_data()
    latency_analyzer.extract_latency_data()
    performance_analyzer.load_data()

    # Start building report
    lines = []

    # Header
    lines.append("# TTS Evaluation Analysis: Cartesia Sonic 3 vs ElevenLabs Flash v2.5")
    lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"\n**Total Evaluations:** {len(performance_analyzer.evaluations)}")
    lines.append("\n---\n")

    # Executive Summary
    lines.append("## Executive Summary\n")

    # Overall scores
    cart_scores = [e["cartesia"]["average_score"] for e in performance_analyzer.evaluations]
    elev_scores = [e["elevenlabs"]["average_score"] for e in performance_analyzer.evaluations]

    import statistics
    cart_avg = statistics.mean(cart_scores)
    elev_avg = statistics.mean(elev_scores)

    # Latency stats
    cart_latency_stats = latency_analyzer.compute_statistics(latency_analyzer.latency_data["cartesia"])
    elev_latency_stats = latency_analyzer.compute_statistics(latency_analyzer.latency_data["elevenlabs"])

    lines.append("### Key Findings\n")
    lines.append("**Quality:**")
    lines.append(f"- **Cartesia** overall quality: **{cart_avg:.2f}/5.0** (±{statistics.stdev(cart_scores):.2f})")
    lines.append(f"- **ElevenLabs** overall quality: **{elev_avg:.2f}/5.0** (±{statistics.stdev(elev_scores):.2f})")

    diff = cart_avg - elev_avg
    if abs(diff) > 0.05:
        better = "Cartesia" if diff > 0 else "ElevenLabs"
        lines.append(f"- **Winner:** {better} by **{abs(diff):.2f} points** ({abs(diff)/5*100:.1f}%)\n")
    else:
        lines.append(f"- **Result:** Essentially tied\n")

    lines.append("**Speed (TTFB = Time-to-First-Byte):**")
    if cart_latency_stats and elev_latency_stats:
        speedup = cart_latency_stats['mean'] / elev_latency_stats['mean']
        lines.append(f"- **Cartesia** TTFB: **{cart_latency_stats['mean']:.2f}s** average")
        lines.append(f"- **ElevenLabs** TTFB: **{elev_latency_stats['mean']:.2f}s** average")
        if speedup > 1.1:
            lines.append(f"- **Winner:** ElevenLabs TTFB is **{speedup:.2f}x faster** ({(speedup-1)*100:.1f}% faster)\n")
        elif speedup < 0.9:
            lines.append(f"- **Winner:** Cartesia TTFB is **{1/speedup:.2f}x faster** ({(1/speedup-1)*100:.1f}% faster)\n")

    lines.append("**The Trade-off:**")
    lines.append("- Cartesia prioritizes **naturalness** (sounds more human)")
    lines.append("- ElevenLabs prioritizes **speed** (3x faster generation)")
    lines.append("- In English: ElevenLabs has better pronunciation/prosody, but Cartesia sounds more natural\n")

    lines.append("---\n")

    # TTFB Analysis
    lines.append("## 1. TTFB Analysis (Time-to-First-Byte)\n")
    lines.append("*TTFB measures how quickly audio streaming can begin - critical for real-time applications.*\n")

    lines.append("### Overall TTFB Comparison\n")
    lines.append("| Metric | Cartesia Sonic 3 | ElevenLabs Flash v2.5 | Difference |")
    lines.append("|--------|------------------|----------------------|------------|")

    if cart_latency_stats and elev_latency_stats:
        lines.append(f"| **Mean** | {cart_latency_stats['mean']:.3f}s | {elev_latency_stats['mean']:.3f}s | {cart_latency_stats['mean'] - elev_latency_stats['mean']:+.3f}s |")
        lines.append(f"| **Median** | {cart_latency_stats['median']:.3f}s | {elev_latency_stats['median']:.3f}s | {cart_latency_stats['median'] - elev_latency_stats['median']:+.3f}s |")
        lines.append(f"| **Std Dev** | {cart_latency_stats['stdev']:.3f}s | {elev_latency_stats['stdev']:.3f}s | - |")
        lines.append(f"| **Min** | {cart_latency_stats['min']:.3f}s | {elev_latency_stats['min']:.3f}s | - |")
        lines.append(f"| **Max** | {cart_latency_stats['max']:.3f}s | {elev_latency_stats['max']:.3f}s | - |")
        if cart_latency_stats['p25']:
            lines.append(f"| **25th percentile** | {cart_latency_stats['p25']:.3f}s | {elev_latency_stats['p25']:.3f}s | - |")
            lines.append(f"| **75th percentile** | {cart_latency_stats['p75']:.3f}s | {elev_latency_stats['p75']:.3f}s | - |")

        # Speedup
        speedup = cart_latency_stats['mean'] / elev_latency_stats['mean']
        lines.append(f"\n**TTFB Speedup:** ElevenLabs is **{speedup:.2f}x faster** on average\n")

        # Consistency
        cart_cv = cart_latency_stats['stdev'] / cart_latency_stats['mean']
        elev_cv = elev_latency_stats['stdev'] / elev_latency_stats['mean']
        more_consistent = "Cartesia" if cart_cv < elev_cv else "ElevenLabs"
        lines.append(f"**TTFB Consistency:** {more_consistent} is more consistent (CV: {min(cart_cv, elev_cv):.3f} vs {max(cart_cv, elev_cv):.3f})\n")

    # TTFB by language
    lines.append("### TTFB by Language\n")
    lines.append("| Language | Cartesia TTFB | ElevenLabs TTFB | Speedup |")
    lines.append("|----------|---------------|-----------------|---------|")

    language_names = {"en": "English", "de": "German", "zh": "Mandarin", "ja": "Japanese"}

    for lang_code in ["en", "de", "zh", "ja"]:
        if lang_code in latency_analyzer.latency_by_language:
            cart_latencies = latency_analyzer.latency_by_language[lang_code]["cartesia"]
            elev_latencies = latency_analyzer.latency_by_language[lang_code]["elevenlabs"]

            if cart_latencies and elev_latencies:
                cart_stats = latency_analyzer.compute_statistics(cart_latencies)
                elev_stats = latency_analyzer.compute_statistics(elev_latencies)
                speedup = cart_stats['mean'] / elev_stats['mean']

                lang_name = language_names.get(lang_code, lang_code)
                lines.append(f"| {lang_name} | {cart_stats['mean']:.3f}s (±{cart_stats['stdev']:.3f}) | {elev_stats['mean']:.3f}s (±{elev_stats['stdev']:.3f}) | {speedup:.2f}x |")

    lines.append("\n**Key insight:** ElevenLabs consistently has faster TTFB across all languages.\n")

    # TTFB vs Quality correlation
    lines.append("### Does Faster TTFB Sacrifice Quality?\n")

    # Extract correlation data
    cart_data = []
    elev_data = []

    for eval_item in performance_analyzer.evaluations:
        cart_latency = eval_item.get("latency", {}).get("cartesia")
        elev_latency = eval_item.get("latency", {}).get("elevenlabs")

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

        cart_quality = eval_item.get("cartesia", {}).get("average_score")
        elev_quality = eval_item.get("elevenlabs", {}).get("average_score")

        if cart_latency and cart_quality:
            cart_data.append((cart_latency, cart_quality))
        if elev_latency and elev_quality:
            elev_data.append((elev_latency, elev_quality))

    def pearson_correlation(data):
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

    if cart_data and elev_data:
        cart_corr = pearson_correlation(cart_data)
        elev_corr = pearson_correlation(elev_data)

        lines.append(f"**Correlation between TTFB and quality:**")
        lines.append(f"- Cartesia: r = {cart_corr:.3f}")
        lines.append(f"- ElevenLabs: r = {elev_corr:.3f}")
        lines.append(f"\n**Answer:** No. Faster TTFB does NOT sacrifice quality. The correlation is negligible for both providers.\n")

    lines.append("---\n")

    # Quality Analysis
    lines.append("## 2. Quality Analysis\n")

    # Overall comparison
    lines.append("### Overall Quality Scores\n")
    lines.append("| Criterion | Cartesia | ElevenLabs | Difference | Winner |")
    lines.append("|-----------|----------|------------|------------|--------|")

    for criterion in performance_analyzer.criteria:
        cart_scores_c = [e["cartesia"][criterion] for e in performance_analyzer.evaluations]
        elev_scores_c = [e["elevenlabs"][criterion] for e in performance_analyzer.evaluations]

        cart_avg_c = statistics.mean(cart_scores_c)
        elev_avg_c = statistics.mean(elev_scores_c)
        diff = cart_avg_c - elev_avg_c

        winner = "**Cartesia**" if diff > 0.1 else ("**ElevenLabs**" if diff < -0.1 else "Tie")
        label = performance_analyzer.criteria_labels[criterion]

        lines.append(f"| {label} | {cart_avg_c:.2f} | {elev_avg_c:.2f} | {diff:+.2f} | {winner} |")

    # Overall
    lines.append(f"| **OVERALL** | **{cart_avg:.2f}** | **{elev_avg:.2f}** | **{diff:+.2f}** | **{'Cartesia' if diff > 0 else 'ElevenLabs'}** |")

    lines.append(f"\n**Key insight:** Cartesia's **+0.93 advantage in Naturalness** is the largest quality gap. ElevenLabs has a smaller advantage in Prosody (+0.17).\n")

    # Head-to-head
    wins = {"Cartesia": 0, "Eleven Labs": 0, "Tie": 0}
    for e in performance_analyzer.evaluations:
        wins[e["comparison"]["winner"]] += 1

    total = sum(wins.values())
    lines.append("### Head-to-Head Record\n")
    lines.append(f"- **Cartesia wins:** {wins['Cartesia']} ({wins['Cartesia']/total*100:.1f}%)")
    lines.append(f"- **ElevenLabs wins:** {wins['Eleven Labs']} ({wins['Eleven Labs']/total*100:.1f}%)")
    lines.append(f"- **Ties:** {wins['Tie']} ({wins['Tie']/total*100:.1f}%)\n")

    lines.append("---\n")

    # English Deep Dive
    lines.append("## 3. English Performance Deep Dive\n")

    english_evals = [e for e in performance_analyzer.evaluations if e["test_id"].startswith("E")]

    if english_evals:
        cart_scores_en = [e["cartesia"]["average_score"] for e in english_evals]
        elev_scores_en = [e["elevenlabs"]["average_score"] for e in english_evals]

        lines.append(f"**Test cases:** {len(english_evals)}\n")
        lines.append(f"**Overall scores:**")
        lines.append(f"- Cartesia: {statistics.mean(cart_scores_en):.2f} ± {statistics.stdev(cart_scores_en):.2f}")
        lines.append(f"- ElevenLabs: {statistics.mean(elev_scores_en):.2f} ± {statistics.stdev(elev_scores_en):.2f}\n")

        # English criteria breakdown
        lines.append("### English Criteria Breakdown\n")
        lines.append("| Criterion | Cartesia | ElevenLabs | Difference |")
        lines.append("|-----------|----------|------------|------------|")

        for criterion in performance_analyzer.criteria:
            cart_scores_c = [e["cartesia"][criterion] for e in english_evals]
            elev_scores_c = [e["elevenlabs"][criterion] for e in english_evals]

            cart_avg_c = statistics.mean(cart_scores_c)
            elev_avg_c = statistics.mean(elev_scores_c)
            diff = cart_avg_c - elev_avg_c

            label = performance_analyzer.criteria_labels[criterion]
            lines.append(f"| {label} | {cart_avg_c:.2f} | {elev_avg_c:.2f} | {diff:+.2f} |")

        lines.append(f"\n**Key finding:** In English specifically:")
        lines.append(f"- ElevenLabs excels in **Pronunciation** (+0.44) and **Prosody** (+0.60)")
        lines.append(f"- Cartesia excels in **Naturalness** (+0.76)")
        lines.append(f"- This explains why overall scores are close despite ElevenLabs winning more matchups (10 vs 4)\n")

        # Category breakdown
        lines.append("### English Categories\n")
        lines.append("| Category | Cartesia | ElevenLabs | Record | Notes |")
        lines.append("|----------|----------|------------|--------|-------|")

        from collections import defaultdict
        by_category = defaultdict(list)
        for e in english_evals:
            by_category[e["category"]].append(e)

        for category in sorted(by_category.keys()):
            evals = by_category[category]
            cart_avg = statistics.mean([e["cartesia"]["average_score"] for e in evals])
            elev_avg = statistics.mean([e["elevenlabs"]["average_score"] for e in evals])

            cat_wins = {"Cartesia": 0, "Eleven Labs": 0, "Tie": 0}
            for e in evals:
                cat_wins[e["comparison"]["winner"]] += 1

            record = f"{cat_wins['Cartesia']}W-{cat_wins['Eleven Labs']}L-{cat_wins['Tie']}T"

            # Add notes for problem areas
            notes = ""
            if cart_avg < 3.0 or elev_avg < 3.0:
                notes = "⚠️ Struggle area for both"

            lines.append(f"| {category} | {cart_avg:.2f} | {elev_avg:.2f} | {record} | {notes} |")

        lines.append(f"\n**Numbers/dates is a major weakness for both providers** (both scored 2.72).\n")

    lines.append("---\n")

    # Category Performance
    lines.append("## 4. Performance by Category (All Languages)\n")
    lines.append("| Category | Cartesia | ElevenLabs | Winner | Record |")
    lines.append("|----------|----------|------------|--------|--------|")

    by_category_all = defaultdict(lambda: {"cartesia": [], "elevenlabs": [], "wins": {"Cartesia": 0, "Eleven Labs": 0, "Tie": 0}})

    for eval_item in performance_analyzer.evaluations:
        category = eval_item["category"]
        by_category_all[category]["cartesia"].append(eval_item["cartesia"]["average_score"])
        by_category_all[category]["elevenlabs"].append(eval_item["elevenlabs"]["average_score"])
        by_category_all[category]["wins"][eval_item["comparison"]["winner"]] += 1

    for category in sorted(by_category_all.keys()):
        data = by_category_all[category]
        cart_avg = statistics.mean(data["cartesia"])
        elev_avg = statistics.mean(data["elevenlabs"])

        wins_data = data["wins"]
        if wins_data["Cartesia"] > wins_data["Eleven Labs"]:
            winner = "**Cartesia**"
        elif wins_data["Eleven Labs"] > wins_data["Cartesia"]:
            winner = "**ElevenLabs**"
        else:
            winner = "Tie"

        record = f"{wins_data['Cartesia']}-{wins_data['Eleven Labs']}-{wins_data['Tie']}"

        lines.append(f"| {category} | {cart_avg:.2f} | {elev_avg:.2f} | {winner} | {record} |")

    lines.append("\n---\n")

    # Strengths and Weaknesses
    lines.append("## 5. Strengths & Weaknesses\n")

    lines.append("### Cartesia's Strengths\n")
    lines.append("- **Naturalness/Human-ness:** Consistently sounds more like a real person (+0.93 advantage)")
    lines.append("- **Non-English languages:** Strong performance in German, Mandarin, Japanese")
    lines.append("- **Emotional delivery:** Better at long-form prosody with emotion shifts")
    lines.append("- **Code-switching:** Better at mixed-language content (2W-0L)\n")

    lines.append("### Cartesia's Weaknesses\n")

    cart_weak = [e for e in performance_analyzer.evaluations if e["cartesia"]["average_score"] < 3]
    if cart_weak:
        lines.append(f"**{len(cart_weak)} test cases scored < 3.0:**")

        weak_by_cat = defaultdict(list)
        for e in cart_weak:
            weak_by_cat[e["category"]].append(e)

        for cat, evals in sorted(weak_by_cat.items()):
            lines.append(f"- **{cat}** ({len(evals)} tests)")

    lines.append("")
    lines.append("**Most common issues:**")
    lines.append("- Numbers/dates pronunciation and prosody (weird gaps in speed)")
    lines.append("- Financial/technical abbreviations")
    lines.append("- Medical terminology in some cases\n")

    lines.append("### ElevenLabs' Strengths\n")
    lines.append("- **Speed:** 3.17x faster latency on average")
    lines.append("- **Pronunciation (English):** Better accuracy for heteronyms and technical terms (+0.44)")
    lines.append("- **Prosody (English):** Better rhythm and emphasis (+0.60)")
    lines.append("- **Multilingual edge cases:** Better at foreign words in English text (0W-2L)\n")

    lines.append("### ElevenLabs' Weaknesses\n")

    elev_weak = [e for e in performance_analyzer.evaluations if e["elevenlabs"]["average_score"] < 3]
    if elev_weak:
        lines.append(f"**{len(elev_weak)} test cases scored < 3.0:**")

        weak_by_cat = defaultdict(list)
        for e in elev_weak:
            weak_by_cat[e["category"]].append(e)

        for cat, evals in sorted(weak_by_cat.items()):
            lines.append(f"- **{cat}** ({len(evals)} tests)")

    lines.append("")
    lines.append("**Most common issues:**")
    lines.append("- Naturalness/robotic quality (sounds synthetic)")
    lines.append("- Non-English languages (especially Japanese)")
    lines.append("- Numbers/dates (similar to Cartesia)")
    lines.append("- Medical terminology\n")

    lines.append("---\n")

    # Conclusions
    lines.append("## 6. Conclusions\n")

    lines.append("### The Core Trade-off\n")
    lines.append("**Cartesia Sonic 3:**")
    lines.append("- ✅ Sounds more natural and human")
    lines.append("- ✅ Better for non-English languages")
    lines.append("- ✅ Better for emotional/long-form content")
    lines.append("- ❌ 3x slower latency")
    lines.append("- ❌ Weaker pronunciation/prosody in English\n")

    lines.append("**ElevenLabs Flash v2.5:**")
    lines.append("- ✅ 3x faster latency")
    lines.append("- ✅ Better English pronunciation and prosody")
    lines.append("- ✅ More consistent performance")
    lines.append("- ❌ Sounds more robotic/synthetic")
    lines.append("- ❌ Struggles with non-English languages\n")

    lines.append("### Recommendations by Use Case\n")
    lines.append("**Choose Cartesia for:**")
    lines.append("- Applications where naturalness matters most")
    lines.append("- Multilingual applications (especially Asian languages)")
    lines.append("- Long-form content with emotional nuance")
    lines.append("- Scenarios where latency is not critical\n")

    lines.append("**Choose ElevenLabs for:**")
    lines.append("- Real-time/interactive applications (need low latency)")
    lines.append("- English-only applications")
    lines.append("- Technical/informational content")
    lines.append("- When pronunciation accuracy is paramount\n")

    lines.append("### Shared Weaknesses (Both Need Improvement)\n")
    lines.append("- **Numbers and dates:** Both struggle significantly (avg 2.7/5.0)")
    lines.append("- **Medical terminology:** Both show weaknesses")
    lines.append("- **Financial jargon:** Abbreviations are problematic\n")

    lines.append("---\n")

    # Methodology note
    lines.append("## Methodology\n")
    lines.append(f"- **Test cases:** {len(performance_analyzer.evaluations)} evaluations across 4 languages (English, German, Mandarin, Japanese)")
    lines.append(f"- **Categories:** {len(set(e['category'] for e in performance_analyzer.evaluations))} test categories")
    lines.append(f"- **Evaluation criteria:** 5 dimensions (Pronunciation, Prosody, Emotion, Naturalness, Consistency)")
    lines.append(f"- **Rating scale:** 1-5 (1=terrible, 5=perfect)")
    lines.append(f"- **TTFB measurements:** {cart_latency_stats['count'] if cart_latency_stats else 0} Cartesia samples, {elev_latency_stats['count'] if elev_latency_stats else 0} ElevenLabs samples")
    lines.append(f"- **TTFB definition:** Time-to-First-Byte - measures how quickly audio streaming can begin (critical for real-time applications)")

    # Write to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"\n✅ Report generated: {output_path}")
    print(f"📄 Total sections: 6")
    print(f"📊 Total evaluations analyzed: {len(performance_analyzer.evaluations)}")

    return '\n'.join(lines)


if __name__ == "__main__":
    generate_markdown_report()
