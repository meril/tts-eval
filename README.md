# TTS Evaluation Framework: Cartesia vs ElevenLabs

A comprehensive evaluation framework for comparing Cartesia Sonic 3 and ElevenLabs Flash v2.5 text-to-speech models.

**[View Live Demo](https://tts-model-eval-results.vercel.app)** - Listen to audio comparisons and see evaluation results

## Overview

This framework provides:
- **Structured test cases** across multiple languages (English, German, Mandarin, Japanese)
- **Automated audio generation** using both Cartesia and ElevenLabs APIs
- **Interactive evaluation interface** for manual listening and scoring
- **Analysis and reporting** tools for quantitative comparison

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file or edit `config.yaml`:

```yaml
api_keys:
  cartesia: "YOUR_CARTESIA_API_KEY"
  elevenlabs: "YOUR_ELEVENLABS_API_KEY"
```

### 3. Set Voice IDs

Update voice IDs for each language in `config.yaml`:

```yaml
models:
  cartesia:
    language_voices:
      en: "your-english-voice-id"
  elevenlabs:
    language_voices:
      en: "your-english-voice-id"
```

### 4. Generate Audio Files

```bash
./run.sh scripts/generate_audio.py --languages en
```

### 5. Run Evaluation Interface

```bash
./run.sh scripts/evaluate.py --language en
```

### 6. Generate Analysis Report

```bash
python3 scripts/generate_report.py
```

## Project Structure

```
tts-eval/
├── config.yaml              # Configuration and API settings
├── requirements.txt         # Python dependencies
├── test_cases/              # Test cases by language
│   ├── english.json
│   ├── german.json
│   ├── mandarin.json
│   └── japanese.json
├── outputs/                 # Generated audio files
│   ├── cartesia/
│   └── elevenlabs/
├── scripts/                 # Main scripts
│   ├── generate_audio.py    # Batch audio generation
│   ├── evaluate.py          # Interactive evaluation UI
│   ├── analyze_latency.py   # Latency analysis
│   ├── analyze_performance.py # Quality analysis
│   └── generate_report.py   # Report generation
├── results/                 # Evaluation results
│   ├── evaluations.json
│   └── analysis_report.md
└── vercel-site/             # Static site for sharing results
```

## Evaluation Criteria

Each audio sample is rated on a **1-5 scale** for:

| Criterion | Description |
|-----------|-------------|
| **Pronunciation Accuracy** | Correct phonemes, heteronyms, polyphones |
| **Prosody** | Natural rhythm, stress, intonation patterns |
| **Emotional Appropriateness** | Matches intended tone/sentiment |
| **Naturalness** | Sounds like a native speaker |
| **Consistency** | Same quality across generations |



## License

MIT
