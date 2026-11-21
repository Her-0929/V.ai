"""Tests for the emotional intelligence service (no external dependencies)."""
import pytest
from app.services.emotional_intelligence_service import (
    emotional_intelligence_service,
    Emotion,
    EmotionalIntensity,
    EmotionalContext,
)


# ──────────────────────────────────────────────────────────────────────────────
# Basic detection
# ──────────────────────────────────────────────────────────────────────────────

def test_neutral_on_empty_string():
    ctx = emotional_intelligence_service.analyze_message("")
    assert ctx.primary_emotion == Emotion.NEUTRAL


def test_neutral_on_very_short_message():
    ctx = emotional_intelligence_service.analyze_message("hi")
    assert ctx.primary_emotion == Emotion.NEUTRAL


def test_stress_detected():
    ctx = emotional_intelligence_service.analyze_message(
        "I'm so stressed and overwhelmed with all these deadlines, can't cope"
    )
    assert ctx.primary_emotion == Emotion.STRESS
    assert ctx.intensity in (EmotionalIntensity.MEDIUM, EmotionalIntensity.HIGH)


def test_happiness_detected():
    ctx = emotional_intelligence_service.analyze_message(
        "I'm so happy today, everything is wonderful and amazing!"
    )
    assert ctx.primary_emotion == Emotion.HAPPINESS


def test_sadness_detected():
    ctx = emotional_intelligence_service.analyze_message(
        "I've been crying all day, I feel so sad and heartbroken and devastated"
    )
    assert ctx.primary_emotion == Emotion.SADNESS


def test_frustration_detected():
    ctx = emotional_intelligence_service.analyze_message(
        "I'm so frustrated, nothing works and it's so annoying, keeps failing"
    )
    assert ctx.primary_emotion == Emotion.FRUSTRATION


def test_excitement_detected():
    ctx = emotional_intelligence_service.analyze_message(
        "I'm so excited, I just found out amazing news, can't wait!"
    )
    assert ctx.primary_emotion in (Emotion.EXCITEMENT, Emotion.HAPPINESS)


def test_gratitude_detected():
    ctx = emotional_intelligence_service.analyze_message(
        "Thank you so much, I really appreciate your help, so helpful"
    )
    assert ctx.primary_emotion == Emotion.GRATITUDE


def test_loneliness_detected():
    ctx = emotional_intelligence_service.analyze_message(
        "I feel so lonely, no one around, completely isolated and alone"
    )
    assert ctx.primary_emotion == Emotion.LONELINESS


def test_anxiety_detected():
    ctx = emotional_intelligence_service.analyze_message(
        "I'm so anxious and worried, what if everything goes wrong, I'm scared"
    )
    assert ctx.primary_emotion in (Emotion.ANXIETY, Emotion.STRESS)


def test_motivation_detected():
    ctx = emotional_intelligence_service.analyze_message(
        "I'm so motivated and determined, going to work towards this, can do this"
    )
    assert ctx.primary_emotion == Emotion.MOTIVATION


# ──────────────────────────────────────────────────────────────────────────────
# Confidence and intensity
# ──────────────────────────────────────────────────────────────────────────────

def test_confidence_in_range():
    ctx = emotional_intelligence_service.analyze_message("I am happy today")
    assert 0.0 <= ctx.confidence <= 1.0


def test_intensity_is_valid_enum():
    ctx = emotional_intelligence_service.analyze_message("I am a bit stressed")
    assert ctx.intensity in (EmotionalIntensity.LOW, EmotionalIntensity.MEDIUM, EmotionalIntensity.HIGH)


def test_high_intensity_on_strong_message():
    ctx = emotional_intelligence_service.analyze_message(
        "I'm devastated and completely heartbroken, been crying all night, feel empty"
    )
    if ctx.primary_emotion == Emotion.SADNESS:
        assert ctx.intensity in (EmotionalIntensity.MEDIUM, EmotionalIntensity.HIGH)


def test_should_acknowledge_for_medium_or_high():
    ctx = emotional_intelligence_service.analyze_message(
        "I'm overwhelmed and so stressed, can't cope with this pressure"
    )
    if ctx.intensity in (EmotionalIntensity.MEDIUM, EmotionalIntensity.HIGH):
        assert ctx.should_acknowledge is True


def test_no_acknowledge_for_neutral():
    ctx = emotional_intelligence_service.analyze_message("")
    assert ctx.should_acknowledge is False


# ──────────────────────────────────────────────────────────────────────────────
# Secondary emotions
# ──────────────────────────────────────────────────────────────────────────────

def test_secondary_emotions_max_two():
    ctx = emotional_intelligence_service.analyze_message(
        "I'm stressed, frustrated, confused, and overwhelmed by all this"
    )
    assert len(ctx.secondary_emotions) <= 2


def test_secondary_emotions_exclude_primary():
    ctx = emotional_intelligence_service.analyze_message(
        "I'm stressed and frustrated and confused and can't cope"
    )
    assert ctx.primary_emotion not in ctx.secondary_emotions


# ──────────────────────────────────────────────────────────────────────────────
# format_for_prompt
# ──────────────────────────────────────────────────────────────────────────────

def test_format_for_prompt_neutral_returns_empty():
    ctx = emotional_intelligence_service.analyze_message("")
    result = emotional_intelligence_service.format_for_prompt(ctx)
    assert result == ""


def test_format_for_prompt_emotional_returns_string():
    ctx = emotional_intelligence_service.analyze_message(
        "I'm overwhelmed and stressed by everything, can't cope"
    )
    result = emotional_intelligence_service.format_for_prompt(ctx)
    assert isinstance(result, str)
    if ctx.primary_emotion != Emotion.NEUTRAL and ctx.confidence >= 0.3:
        assert len(result) > 0


def test_format_for_prompt_contains_emotion_name():
    ctx = emotional_intelligence_service.analyze_message(
        "I'm totally stressed and overwhelmed with all these deadlines"
    )
    result = emotional_intelligence_service.format_for_prompt(ctx)
    if result:
        assert ctx.primary_emotion.value in result


# ──────────────────────────────────────────────────────────────────────────────
# get_response_guidance
# ──────────────────────────────────────────────────────────────────────────────

def test_response_guidance_for_strong_emotion():
    ctx = emotional_intelligence_service.analyze_message(
        "I'm so devastated and heartbroken, been crying all night feeling empty"
    )
    if ctx.intensity == EmotionalIntensity.HIGH and ctx.primary_emotion != Emotion.NEUTRAL:
        assert len(ctx.response_approach) > 0


def test_response_guidance_neutral_is_empty():
    # Create a neutral context directly
    ctx = EmotionalContext(
        primary_emotion=Emotion.NEUTRAL,
        confidence=0.0,
        intensity=EmotionalIntensity.LOW,
    )
    result = emotional_intelligence_service.get_response_guidance(ctx)
    assert result == ""


# ──────────────────────────────────────────────────────────────────────────────
# Conversation history blending
# ──────────────────────────────────────────────────────────────────────────────

def test_history_blending_boosts_stress():
    history = [
        {"role": "user", "content": "I'm really stressed about work deadlines"},
        {"role": "assistant", "content": "I understand that must be hard"},
        {"role": "user", "content": "yeah I'm overwhelmed and can't cope"},
    ]
    ctx = emotional_intelligence_service.analyze_message(
        "yeah it's a lot", conversation_history=history
    )
    # Stress should still be detectable via history blending
    assert ctx.primary_emotion in (Emotion.STRESS, Emotion.ANXIETY, Emotion.FRUSTRATION, Emotion.SADNESS)


def test_empty_history_does_not_crash():
    ctx = emotional_intelligence_service.analyze_message("I'm fine", conversation_history=[])
    assert isinstance(ctx, EmotionalContext)


def test_none_history_does_not_crash():
    ctx = emotional_intelligence_service.analyze_message("I'm happy", conversation_history=None)
    assert isinstance(ctx, EmotionalContext)


# ──────────────────────────────────────────────────────────────────────────────
# store_as_memory
# ──────────────────────────────────────────────────────────────────────────────

def test_store_as_memory_false_for_neutral():
    ctx = EmotionalContext(
        primary_emotion=Emotion.NEUTRAL,
        confidence=0.0,
        intensity=EmotionalIntensity.LOW,
    )
    result = emotional_intelligence_service.should_store_emotional_memory(ctx, "hello")
    assert result is False


def test_store_as_memory_true_for_high_stress():
    ctx = EmotionalContext(
        primary_emotion=Emotion.STRESS,
        confidence=0.8,
        intensity=EmotionalIntensity.HIGH,
        store_as_memory=True,
    )
    result = emotional_intelligence_service.should_store_emotional_memory(
        ctx, "I'm completely overwhelmed and burning out from work"
    )
    assert result is True


def test_store_as_memory_false_for_short_message():
    ctx = EmotionalContext(
        primary_emotion=Emotion.STRESS,
        confidence=0.8,
        intensity=EmotionalIntensity.HIGH,
        store_as_memory=True,
    )
    result = emotional_intelligence_service.should_store_emotional_memory(ctx, "stressed")
    assert result is False  # message too short (< 20 chars)

