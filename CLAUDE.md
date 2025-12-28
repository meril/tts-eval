# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TTS Evaluation Framework comparing Cartesia Sonic 3 and ElevenLabs Flash v2.5 text-to-speech models. The framework generates audio samples, provides a manual evaluation interface, and produces analysis reports.

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Generate audio for test cases (uses venv Python)
./run.sh scripts/generate_audio.py --languages en
./run.sh scripts/generate_audio.py --languages en de zh ja
./run.sh scripts/generate_audio.py --filter E1-  # Only heteronym tests

# Run interactive evaluation interface (Gradio web UI)
./run.sh scripts/evaluate.py --language en

# Generate analysis report
python3 scripts/generate_report.py

# Check API setup
./run.sh scripts/check_setup.py
```

## Architecture

### Data Flow
1. **Test cases** (`test_cases/*.json`) define evaluation scenarios by language and category
2. **Audio generation** (`scripts/generate_audio.py`) calls both TTS APIs and saves MP3s to `outputs/`
3. **Manual evaluation** (`scripts/evaluate.py`) presents A/B comparisons in a Gradio interface, saves ratings to `results/evaluations.json`
4. **Analysis** (`scripts/generate_report.py`) combines TTFB + quality data into `results/analysis_report.md`

### Key Components
- `scripts/cartesia_client.py` - Cartesia Sonic 3 API client (REST, `/tts/bytes` endpoint, streams response to measure TTFB)
- `scripts/elevenlabs_client.py` - ElevenLabs Flash v2.5 API client (streams response to measure TTFB)
- `scripts/generate_audio.py` - `AudioGenerator` orchestrates batch generation with progress tracking
- `scripts/evaluate.py` - `EvaluationInterface` Gradio app for blind A/B testing with 5 criteria
- `scripts/analyze_latency.py` - `LatencyAnalyzer` for TTFB (Time-to-First-Byte) statistics
- `scripts/analyze_performance.py` - `PerformanceAnalyzer` for quality score analysis

### Latency Measurement
The clients measure **TTFB (Time-to-First-Byte)** - the time until the first audio chunk arrives. This is critical for real-time streaming applications. Both `ttfb` and `total_time` are recorded in generation logs.

### Configuration
- `config.yaml` - Model IDs, voice IDs per language, output settings, evaluation criteria
- `.env` - API keys (`CARTESIA_API_KEY`, `ELEVENLABS_API_KEY`)

### Test Case Structure
Test IDs follow pattern: `{Lang}{Category}-{Id}` (e.g., `E1-H1` = English, Category 1, Heteronym 1)
- Language prefixes: E=English, D=German, C=Chinese, J=Japanese
- Categories: heteronyms, numbers_dates, acronyms, medical_domain, financial_domain, prosody_longform, edge_cases

### Evaluation Criteria (1-5 scale)
1. Pronunciation Accuracy
2. Prosody (rhythm, stress, intonation)
3. Emotional Appropriateness
4. Naturalness
5. Consistency

### Static Site
`vercel-site/` contains a deployable static site for sharing audio comparisons and results.
