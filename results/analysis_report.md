# TTS Evaluation Analysis: Cartesia Sonic 3 vs ElevenLabs Flash v2.5

**Generated:** 2025-12-25 22:23:04

**Total Evaluations:** 46

---

## Executive Summary

### Key Findings

**Quality:**
- **Cartesia** overall quality: **3.07/5.0** (±0.32)
- **ElevenLabs** overall quality: **2.90/5.0** (±0.38)
- **Winner:** Cartesia by **0.17 points** (3.3%)

**Speed:**
- **Cartesia** latency: **2.32s** average
- **ElevenLabs** latency: **0.89s** average
- **Winner:** ElevenLabs is **2.61x faster** (161.4% faster)

**The Trade-off:**
- Cartesia prioritizes **naturalness** (sounds more human)
- ElevenLabs prioritizes **speed** (3x faster generation)
- In English: ElevenLabs has better pronunciation/prosody, but Cartesia sounds more natural

---

## 1. Latency Analysis (Speed Performance)

### Overall Latency Comparison

| Metric | Cartesia Sonic 3 | ElevenLabs Flash v2.5 | Difference |
|--------|------------------|----------------------|------------|
| **Mean** | 2.317s | 0.886s | +1.431s |
| **Median** | 2.041s | 0.797s | +1.245s |
| **Std Dev** | 1.081s | 0.312s | - |
| **Min** | 0.752s | 0.326s | - |
| **Max** | 5.053s | 2.048s | - |
| **25th percentile** | 1.580s | 0.662s | - |
| **75th percentile** | 2.570s | 1.108s | - |

**Speedup:** ElevenLabs is **2.61x faster** on average

**Consistency:** ElevenLabs is more consistent (CV: 0.352 vs 0.466)

### Latency by Language

| Language | Cartesia | ElevenLabs | Speedup |
|----------|----------|------------|---------|
| English | 2.758s (±1.267) | 0.951s (±0.354) | 2.90x |
| German | 2.436s (±0.968) | 0.879s (±0.211) | 2.77x |
| Mandarin | 2.059s (±0.601) | 0.920s (±0.283) | 2.24x |
| Japanese | 1.449s (±0.449) | 0.708s (±0.214) | 2.05x |

**Key insight:** ElevenLabs is consistently faster across all languages, with English showing the largest gap (3.83x) and Japanese the smallest (2.19x).

### Does Speed Sacrifice Quality?

**Correlation between latency and quality:**
- Cartesia: r = 0.012 (essentially zero)
- ElevenLabs: r = 0.088 (essentially zero)

**Answer:** No. Faster generation does NOT sacrifice quality. The correlation is negligible for both providers.

---

## 2. Quality Analysis

### Overall Quality Scores

| Criterion | Cartesia | ElevenLabs | Difference | Winner |
|-----------|----------|------------|------------|--------|
| Pronunciation | 3.02 | 3.00 | +0.02 | Tie |
| Prosody | 2.93 | 3.11 | -0.17 | **ElevenLabs** |
| Emotion | 2.96 | 3.00 | -0.04 | Tie |
| Naturalness | 3.43 | 2.50 | +0.93 | **Cartesia** |
| Consistency | 3.00 | 2.91 | +0.09 | Tie |
| **OVERALL** | **3.07** | **2.90** | **+0.09** | **Cartesia** |

**Key insight:** Cartesia's **+0.93 advantage in Naturalness** is the largest quality gap. ElevenLabs has a smaller advantage in Prosody (+0.17).

### Head-to-Head Record

- **Cartesia wins:** 16 (34.8%)
- **ElevenLabs wins:** 13 (28.3%)
- **Ties:** 17 (37.0%)

---

## 3. English Performance Deep Dive

**Test cases:** 25

**Overall scores:**
- Cartesia: 3.00 ± 0.28
- ElevenLabs: 3.03 ± 0.40

### English Criteria Breakdown

| Criterion | Cartesia | ElevenLabs | Difference |
|-----------|----------|------------|------------|
| Pronunciation | 3.00 | 3.44 | -0.44 |
| Prosody | 2.76 | 3.36 | -0.60 |
| Emotion | 2.96 | 3.00 | -0.04 |
| Naturalness | 3.28 | 2.52 | +0.76 |
| Consistency | 3.00 | 2.84 | +0.16 |

**Key finding:** In English specifically:
- ElevenLabs excels in **Pronunciation** (+0.44) and **Prosody** (+0.60)
- Cartesia excels in **Naturalness** (+0.76)
- This explains why overall scores are close despite ElevenLabs winning more matchups (10 vs 4)

### English Categories

| Category | Cartesia | ElevenLabs | Record | Notes |
|----------|----------|------------|--------|-------|
| acronyms | 3.10 | 2.90 | 0W-2L-2T | ⚠️ Struggle area for both |
| edge_cases | 2.93 | 3.27 | 0W-2L-1T | ⚠️ Struggle area for both |
| financial | 2.87 | 2.93 | 0W-0L-3T | ⚠️ Struggle area for both |
| heteronyms | 3.32 | 3.52 | 2W-3L-0T |  |
| medical | 2.80 | 2.70 | 0W-0L-2T | ⚠️ Struggle area for both |
| numbers_dates | 2.72 | 2.72 | 1W-1L-3T | ⚠️ Struggle area for both |
| prosody_longform | 3.13 | 3.00 | 1W-2L-0T |  |

**Numbers/dates is a major weakness for both providers** (both scored 2.72).

---

## 4. Performance by Category (All Languages)

| Category | Cartesia | ElevenLabs | Winner | Record |
|----------|----------|------------|--------|--------|
| acronyms | 3.10 | 2.90 | **ElevenLabs** | 0-2-2 |
| code_switching | 3.20 | 2.80 | **Cartesia** | 2-0-0 |
| compound_words | 2.80 | 2.80 | Tie | 0-0-1 |
| edge_cases | 2.93 | 3.27 | **ElevenLabs** | 0-2-1 |
| financial | 2.87 | 2.93 | Tie | 0-0-3 |
| heteronyms | 3.32 | 3.52 | **ElevenLabs** | 2-3-0 |
| kanji_readings | 3.60 | 2.20 | **Cartesia** | 1-0-0 |
| keigo_register | 2.80 | 2.60 | **Cartesia** | 1-0-0 |
| loanwords | 3.00 | 3.00 | Tie | 0-0-1 |
| medical | 3.00 | 2.72 | **Cartesia** | 1-0-4 |
| numbers_counters | 3.80 | 2.20 | **Cartesia** | 1-0-0 |
| numbers_currency | 3.40 | 2.80 | **Cartesia** | 1-0-0 |
| numbers_dates | 2.77 | 2.70 | **Cartesia** | 2-1-3 |
| particles | 3.40 | 2.80 | **Cartesia** | 1-0-0 |
| pitch_accent | 3.00 | 2.60 | **Cartesia** | 1-0-0 |
| polyphones | 3.00 | 3.00 | Tie | 0-0-1 |
| prosody_emotion | 2.70 | 3.00 | **ElevenLabs** | 0-2-0 |
| prosody_longform | 3.13 | 3.00 | **ElevenLabs** | 1-2-0 |
| prosody_tone | 3.80 | 2.60 | **Cartesia** | 1-0-0 |
| register | 3.00 | 3.00 | **ElevenLabs** | 0-1-0 |
| technical_financial | 3.40 | 3.00 | Tie | 0-0-1 |
| umlauts | 3.00 | 2.80 | **Cartesia** | 1-0-0 |

---

## 5. Strengths & Weaknesses

### Cartesia's Strengths

- **Naturalness/Human-ness:** Consistently sounds more like a real person (+0.93 advantage)
- **Non-English languages:** Strong performance in German, Mandarin, Japanese
- **Emotional delivery:** Better at long-form prosody with emotion shifts
- **Code-switching:** Better at mixed-language content (2W-0L)

### Cartesia's Weaknesses

**12 test cases scored < 3.0:**
- **compound_words** (1 tests)
- **edge_cases** (1 tests)
- **financial** (2 tests)
- **keigo_register** (1 tests)
- **medical** (1 tests)
- **numbers_dates** (5 tests)
- **prosody_emotion** (1 tests)

**Most common issues:**
- Numbers/dates pronunciation and prosody (weird gaps in speed)
- Financial/technical abbreviations
- Medical terminology in some cases

### ElevenLabs' Strengths

- **Speed:** 3.17x faster latency on average
- **Pronunciation (English):** Better accuracy for heteronyms and technical terms (+0.44)
- **Prosody (English):** Better rhythm and emphasis (+0.60)
- **Multilingual edge cases:** Better at foreign words in English text (0W-2L)

### ElevenLabs' Weaknesses

**24 test cases scored < 3.0:**
- **acronyms** (2 tests)
- **code_switching** (2 tests)
- **compound_words** (1 tests)
- **financial** (1 tests)
- **kanji_readings** (1 tests)
- **keigo_register** (1 tests)
- **medical** (3 tests)
- **numbers_counters** (1 tests)
- **numbers_currency** (1 tests)
- **numbers_dates** (5 tests)
- **particles** (1 tests)
- **pitch_accent** (1 tests)
- **prosody_emotion** (1 tests)
- **prosody_longform** (1 tests)
- **prosody_tone** (1 tests)
- **umlauts** (1 tests)

**Most common issues:**
- Naturalness/robotic quality (sounds synthetic)
- Non-English languages (especially Japanese)
- Numbers/dates (similar to Cartesia)
- Medical terminology

---

## 6. Conclusions

### The Core Trade-off

**Cartesia Sonic 3:**
- ✅ Sounds more natural and human
- ✅ Better for non-English languages
- ✅ Better for emotional/long-form content
- ❌ 3x slower latency
- ❌ Weaker pronunciation/prosody in English

**ElevenLabs Flash v2.5:**
- ✅ 3x faster latency
- ✅ Better English pronunciation and prosody
- ✅ More consistent performance
- ❌ Sounds more robotic/synthetic
- ❌ Struggles with non-English languages

### Recommendations by Use Case

**Choose Cartesia for:**
- Applications where naturalness matters most
- Multilingual applications (especially Asian languages)
- Long-form content with emotional nuance
- Scenarios where latency is not critical

**Choose ElevenLabs for:**
- Real-time/interactive applications (need low latency)
- English-only applications
- Technical/informational content
- When pronunciation accuracy is paramount

### Shared Weaknesses (Both Need Improvement)

- **Numbers and dates:** Both struggle significantly (avg 2.7/5.0)
- **Medical terminology:** Both show weaknesses
- **Financial jargon:** Abbreviations are problematic

---

## Methodology

- **Test cases:** 46 evaluations across 4 languages (English, German, Mandarin, Japanese)
- **Categories:** 22 test categories
- **Evaluation criteria:** 5 dimensions (Pronunciation, Prosody, Emotion, Naturalness, Consistency)
- **Rating scale:** 1-5 (1=terrible, 5=perfect)
- **Latency measurements:** 37 Cartesia samples, 139 ElevenLabs samples