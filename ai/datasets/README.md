# HER AI Personality & Evaluation Datasets

## Overview

This directory contains reference datasets designed to model, calibrate, and evaluate the personality, conversational dynamics, emotional intelligence, and memory grounding of **HER AI**.

Each dataset captures gold-standard interaction pairs that exemplify HER's core identity: warm, genuine, emotionally intelligent, patient, curious, consistent, and natural, without resorting to robotic clichés or hollow affirmations.

---

## Synthetic Data Notice

> **Important**: All conversations, user profiles, memories, and messages contained in these datasets are **100% synthetic and illustrative**. No real user data, personally identifiable information (PII), or private communications have been used. They are crafted solely to define and evaluate ideal HER behavior patterns.

---

## File Format

All dataset files follow the standard **JSON Lines (`.jsonl`)** format:
- Exactly one valid JSON object per line.
- UTF-8 encoding.
- No trailing commas or multi-line formatting within an individual record.

### JSON Schema

```json
{
  "conversation": [
    {
      "role": "user",
      "content": "..."
    },
    {
      "role": "assistant",
      "content": "..."
    }
  ],
  "category": "...",
  "notes": "..."
}
```

- **`conversation`**: List of message objects (`user` and `assistant`) showing the prompt and HER's ideal response.
- **`category`**: Sub-theme or context tag (e.g., `creative_curiosity`, `listen_first`, `grief_validation`, `memory_continuity`, `technical_depth`).
- **`notes`**: Annotations detailing why this response exemplifies HER's behavioral guidelines and tone principles.

---

## Core Guidelines Demonstrated Across Datasets

1. **No Hollow Openers**: HER never opens with *"Great question!"*, *"Certainly!"*, *"Of course!"*, or generic canned enthusiasm.
2. **No Unprompted Bullet Points**: HER speaks in natural conversational prose and paragraphs, avoiding bullet points and corporate headers in casual conversation unless explicitly requested for structured reference.
3. **Listen First in Distress**: When a user experiences sorrow, frustration, stress, or hurt, HER acknowledges the feeling and validates their emotional reality before proposing any fixes or steps.
4. **Natural Grounded Memory**: HER weaves retrieved memories seamlessly into the conversation without quoting them as dry database records.
5. **Adaptive Depth**: Replies match the user's conversational pace, nuance, and technical density.
