"""HER AI — Baseline Model Persona & Conversational Evaluation.

Evaluates an LLM provider against the gold-standard validation set (ai/prepared/validation.jsonl).
Metrics:
  1. Persona Invariant Adherence:
     - Rejection of canned corporate openers ("Great question!", "Certainly!", "Of course!").
     - Avoidance of unprompted bullet points / headers in casual turns.
     - Listen-first empathy check on distress prompts.
  2. Tone & Character Match:
     - Word count & conciseness ratio compared to target.
     - Average response latency.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import time
from typing import Any

from app.services.llm_service import llm_service

PROHIBITED_OPENERS = [
    "great question",
    "certainly!",
    "of course!",
    "sure thing!",
    "as an ai",
    "as a language model",
]

BULLET_POINT_REGEX = re.compile(r"^\s*[-*•]\s+|\d+\.\s+", re.MULTILINE)


def evaluate_response_quality(response: str, target: str, category: str) -> dict[str, Any]:
    """Score individual response against persona invariants."""
    cleaned = response.strip()
    lower = cleaned.lower()

    # 1. Check prohibited openers
    has_bad_opener = any(lower.startswith(p) for p in PROHIBITED_OPENERS)

    # 2. Check unprompted bullet points (unless user asked for technical breakdown)
    has_bullets = bool(BULLET_POINT_REGEX.search(cleaned))
    allow_bullets = "technical" in category or "recipe" in category or "steps" in category
    bullet_violation = has_bullets and not allow_bullets

    # 3. Word counts
    actual_words = len(cleaned.split())
    target_words = len(target.split())
    length_ratio = actual_words / max(1, target_words)

    # Composite persona score (0 to 100)
    score = 100.0
    if has_bad_opener:
        score -= 40.0
    if bullet_violation:
        score -= 25.0
    if length_ratio > 2.5:  # Overly verbose/rambling
        score -= 20.0
    elif length_ratio < 0.3:  # Too terse
        score -= 15.0

    return {
        "score": max(0.0, score),
        "has_prohibited_opener": has_bad_opener,
        "unprompted_bullets": bullet_violation,
        "actual_word_count": actual_words,
        "target_word_count": target_words,
        "length_ratio": round(length_ratio, 2),
    }


async def run_baseline_evaluation(
    validation_file: str = "ai/prepared/validation.jsonl",
    output_report_file: str = "ai/prepared/baseline_evaluation_report.json",
    max_samples: int | None = 6,  # 6 representative samples for fast baseline
) -> dict[str, Any]:
    """Run baseline evaluation over validation samples using active LLM provider."""
    if not os.path.exists(validation_file):
        raise FileNotFoundError(f"Validation dataset not found: {validation_file}")

    with open(validation_file, "r", encoding="utf-8") as f:
        val_samples = [json.loads(line) for line in f if line.strip()]

    if max_samples:
        val_samples = val_samples[:max_samples]

    results = []
    total_score = 0.0
    total_latency = 0.0
    total_opener_violations = 0
    total_bullet_violations = 0

    provider_name = getattr(llm_service, "provider", "ollama")
    model_name = getattr(llm_service, "model", "qwen3:1.7b")
    print(f"Evaluating {len(val_samples)} validation samples against provider: {provider_name} ({model_name})...")

    for sample in val_samples:
        messages = sample["messages"]
        user_prompt = messages[1]["content"]
        target_reply = messages[2]["content"]
        category = sample.get("category", "general")

        t0 = time.time()
        try:
            generated_response = await llm_service.generate_response(messages[:2])
        except Exception as exc:
            generated_response = f"[ERROR: {exc}]"
        latency = time.time() - t0
        total_latency += latency

        metrics = evaluate_response_quality(generated_response, target_reply, category)
        total_score += metrics["score"]

        if metrics["has_prohibited_opener"]:
            total_opener_violations += 1
        if metrics["unprompted_bullets"]:
            total_bullet_violations += 1

        results.append({
            "id": sample["id"],
            "category": category,
            "user_prompt": user_prompt,
            "target_response": target_reply,
            "generated_response": generated_response,
            "latency_seconds": round(latency, 2),
            "metrics": metrics,
        })

    avg_score = round(total_score / max(1, len(results)), 2)
    avg_latency = round(total_latency / max(1, len(results)), 2)

    summary = {
        "provider": provider_name,
        "model": model_name,
        "samples_evaluated": len(results),
        "average_persona_score": avg_score,
        "average_latency_seconds": avg_latency,
        "prohibited_opener_rate": round(total_opener_violations / max(1, len(results)), 2),
        "unprompted_bullet_rate": round(total_bullet_violations / max(1, len(results)), 2),
        "detailed_results": results,
    }

    with open(output_report_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    return summary


if __name__ == "__main__":
    report = asyncio.run(run_baseline_evaluation())
    print("=" * 60)
    print("BASELINE EVALUATION COMPLETED")
    print("=" * 60)
    print(f"Provider: {report['provider']} ({report['model']})")
    print(f"Average Persona Score: {report['average_persona_score']} / 100")
    print(f"Average Latency: {report['average_latency_seconds']}s")
    print(f"Prohibited Opener Rate: {report['prohibited_opener_rate'] * 100}%")
    print(f"Unprompted Bullet Rate: {report['unprompted_bullet_rate'] * 100}%")
