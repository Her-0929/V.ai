"""
Emotional Intelligence Service for HER AI
==========================================
Analyses incoming user messages using keyword/phrase pattern matching to detect
the user's emotional state and produce structured guidance for the LLM response.

No heavy NLP libraries are used — detection is intentionally lightweight and
runs entirely in pure Python so it adds zero latency and has no GPU requirement.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class Emotion(str, Enum):
    HAPPINESS = "happiness"
    SADNESS = "sadness"
    STRESS = "stress"
    ANXIETY = "anxiety"
    EXCITEMENT = "excitement"
    FRUSTRATION = "frustration"
    LONELINESS = "loneliness"
    CONFUSION = "confusion"
    MOTIVATION = "motivation"
    DISAPPOINTMENT = "disappointment"
    AFFECTION = "affection"
    GRATITUDE = "gratitude"
    NEUTRAL = "neutral"


class EmotionalIntensity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ---------------------------------------------------------------------------
# Data container
# ---------------------------------------------------------------------------

@dataclass
class EmotionalContext:
    primary_emotion: Emotion
    confidence: float                      # 0.0 – 1.0
    intensity: EmotionalIntensity
    secondary_emotions: list[Emotion]
    relevant_context: str                  # brief note on what triggered this analysis
    response_approach: str                 # recommended guidance for HER's response
    should_acknowledge: bool               # whether HER should explicitly acknowledge the emotion
    store_as_memory: bool                  # whether this is significant enough to store


# ---------------------------------------------------------------------------
# Pattern dictionary
# ---------------------------------------------------------------------------

# Each entry is a list of lowercase substrings / phrases.
# A pattern matches if it appears anywhere in the lowercased message text.
EMOTION_PATTERNS: dict[Emotion, list[str]] = {
    Emotion.HAPPINESS: [
        "happy", "great", "wonderful", "amazing", "love it", "joy",
        "fantastic", "awesome", "thrilled", "delighted", "so good",
        ":)", "😊", "😄", "😁",
    ],
    Emotion.SADNESS: [
        "sad", "unhappy", "depressed", "crying", "tears", "miss you",
        "lost", "alone", "grief", "heartbroken", "devastated",
        "feel empty", "😢", "😭", "💔",
    ],
    Emotion.STRESS: [
        "stressed", "overwhelmed", "too much", "can't cope", "pressure",
        "deadline", "exhausted", "burnt out", "swamped",
        "drowning in", "falling behind",
    ],
    Emotion.ANXIETY: [
        "anxious", "worried", "nervous", "scared", "fear", "panic",
        "dread", "uncertain", "what if", "can't stop thinking",
    ],
    Emotion.EXCITEMENT: [
        "so excited", "can't wait", "amazing news", "just found out",
        "finally", "dream come true", "🎉", "🙌", "pumped", "stoked",
    ],
    Emotion.FRUSTRATION: [
        "frustrated", "annoyed", "irritated", "fed up", "sick of",
        "why won't", "doesn't work", "keeps failing", "nothing works",
        "so annoying",
    ],
    Emotion.LONELINESS: [
        "lonely", "alone", "no one", "nobody", "isolated",
        "miss people", "haven't talked", "by myself", "feel invisible",
    ],
    Emotion.CONFUSION: [
        "confused", "don't understand", "lost", "unclear",
        "makes no sense", "what does", "how do i",
        "not sure how", "can't figure",
    ],
    Emotion.MOTIVATION: [
        "motivated", "ready", "let's do", "determined", "going to",
        "working towards", "making progress", "can do this", "focused",
    ],
    Emotion.DISAPPOINTMENT: [
        "disappointed", "let down", "expected better",
        "didn't work out", "failed", "not what i hoped",
        "wasted", "fell through",
    ],
    Emotion.AFFECTION: [
        "love you", "care about", "mean a lot", "appreciate you",
        "you're wonderful", "you help me so much", "glad i have you",
    ],
    Emotion.GRATITUDE: [
        "thank you", "thanks", "grateful", "appreciate",
        "helped me", "means a lot", "so helpful",
    ],
    # NEUTRAL has no patterns — it is the default fallback
    Emotion.NEUTRAL: [],
}

# Emotions whose HIGH-intensity occurrences are worth persisting as memories
_MEMORY_WORTHY_EMOTIONS: set[Emotion] = {
    Emotion.SADNESS,
    Emotion.STRESS,
    Emotion.DISAPPOINTMENT,
    Emotion.EXCITEMENT,
    Emotion.MOTIVATION,
}


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class EmotionalIntelligenceService:
    """
    Detects the emotional state of a user message via pattern matching and
    returns structured guidance to inform HER's response style and memory
    storage decisions.

    The service is stateless — every call is independent.
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze_message(
        self,
        message: str,
        conversation_history: list[dict] | None = None,
    ) -> EmotionalContext:
        """
        Analyse *message* and return an :class:`EmotionalContext`.

        Parameters
        ----------
        message:
            The raw user message (any length, may contain emoji).
        conversation_history:
            Optional list of chat-history dicts.  Each dict is expected to
            have at least ``"role"`` (``"user"`` | ``"assistant"``) and
            ``"content"`` keys, matching the format used by llm_service.
        """
        # --- Edge-case guard: treat empty / very short input as neutral ----
        if not message or len(message.strip()) < 5:
            return self._neutral_context("Message too short for analysis.")

        # 1. Keyword analysis on current message (lowercased)
        current_text: str = message.lower()
        current_scores: dict[Emotion, float] = self._keyword_analysis(current_text)

        # 2. Optionally blend with lightweight analysis of recent history
        if conversation_history:
            history_scores = self._history_analysis(conversation_history)
            # Blend: 70 % current, 30 % history
            blended: dict[Emotion, float] = {}
            for emotion in Emotion:
                blended[emotion] = (
                    0.7 * current_scores.get(emotion, 0.0)
                    + 0.3 * history_scores.get(emotion, 0.0)
                )
            raw_scores = blended
        else:
            raw_scores = current_scores

        # 3. Normalise so the strongest signal == 1.0
        normalized: dict[Emotion, float] = self._normalize_scores(raw_scores)

        # 4. Identify the dominant emotion
        # Sort by normalised score descending, skipping NEUTRAL (it's the fallback)
        ranked: list[tuple[Emotion, float]] = sorted(
            ((e, s) for e, s in normalized.items() if e != Emotion.NEUTRAL),
            key=lambda t: t[1],
            reverse=True,
        )

        top_emotion: Emotion
        top_score: float
        second_score: float

        if ranked and ranked[0][1] > 0:
            top_emotion, top_score = ranked[0]
            second_score = ranked[1][1] if len(ranked) > 1 else 0.0
        else:
            # No signal at all → neutral
            return self._neutral_context("No emotional signals detected.")

        # Total raw signal count for the primary emotion (pre-normalisation)
        raw_top_count: float = raw_scores[top_emotion]

        # 5. Confidence
        confidence: float
        if top_score > second_score * 1.5 and raw_top_count >= 2:
            # Clear leader with multiple corroborating signals
            confidence = min(0.9, 0.5 + 0.1 * raw_top_count)
        elif top_score > 0:
            confidence = 0.5
        else:
            confidence = 0.2

        # 6. Intensity
        intensity: EmotionalIntensity
        if confidence > 0.7 and raw_top_count > 3:
            intensity = EmotionalIntensity.HIGH
        elif raw_top_count >= 2 or confidence > 0.4:
            intensity = EmotionalIntensity.MEDIUM
        else:
            intensity = EmotionalIntensity.LOW

        # 7. Secondary emotions (up to 2, score > 0, excluding primary)
        secondary_emotions: list[Emotion] = [
            e for e, s in ranked[1:]
            if s > 0 and e != top_emotion
        ][:2]

        # 8. Acknowledgement flag
        should_acknowledge: bool = (
            intensity in (EmotionalIntensity.MEDIUM, EmotionalIntensity.HIGH)
            and top_emotion != Emotion.NEUTRAL
        )

        # 9. Memory-storage flag
        store_as_memory: bool = (
            intensity == EmotionalIntensity.HIGH
            and top_emotion in _MEMORY_WORTHY_EMOTIONS
        )

        # 10. Human-readable context note
        relevant_context: str = (
            f"Detected '{top_emotion.value}' via keyword analysis "
            f"(raw signals: {int(raw_top_count)}, confidence: {confidence:.2f})."
        )

        # 11. Build a preliminary context so get_response_guidance can inspect it
        ctx = EmotionalContext(
            primary_emotion=top_emotion,
            confidence=confidence,
            intensity=intensity,
            secondary_emotions=secondary_emotions,
            relevant_context=relevant_context,
            response_approach="",          # filled in next
            should_acknowledge=should_acknowledge,
            store_as_memory=store_as_memory,
        )

        # 12. Response guidance
        ctx.response_approach = self.get_response_guidance(ctx)

        return ctx

    # ------------------------------------------------------------------

    def get_response_guidance(self, context: EmotionalContext) -> str:
        """
        Return a natural-language instruction string that tells HER *how* to
        respond given the detected emotional state and intensity.
        """
        emotion = context.primary_emotion
        intensity = context.intensity

        if emotion == Emotion.NEUTRAL:
            return ""

        if emotion == Emotion.SADNESS:
            if intensity == EmotionalIntensity.HIGH:
                return (
                    "The user seems to be going through something painful. "
                    "Listen first. Acknowledge their feelings warmly before "
                    "anything else. Don't offer solutions unless asked."
                )
            return "The user may be a bit down. Be warm and attentive."

        if emotion == Emotion.STRESS:
            if intensity == EmotionalIntensity.HIGH:
                return (
                    "The user seems overwhelmed. Respond calmly and gently. "
                    "Help them feel less alone with the situation."
                )
            return "The user seems stressed. Be calm and grounding."

        if emotion == Emotion.ANXIETY:
            return (
                "The user may be anxious. Be reassuring and clear. "
                "Avoid adding more complexity or unknowns."
            )

        if emotion in (Emotion.HAPPINESS, Emotion.EXCITEMENT):
            if intensity == EmotionalIntensity.HIGH:
                return (
                    "The user is in a great mood or excited. "
                    "Match their energy. Be enthusiastic and warm."
                )
            return "The user seems happy. Be warm and positive."

        if emotion == Emotion.FRUSTRATION:
            return (
                "The user is frustrated. Validate their frustration before "
                "anything else. Don't be dismissive."
            )

        if emotion == Emotion.LONELINESS:
            return (
                "The user may be feeling alone. Be present and warm. "
                "Listening matters most right now."
            )

        if emotion == Emotion.CONFUSION:
            return (
                "The user is confused. Be clear and patient. "
                "Break things down simply."
            )

        if emotion == Emotion.MOTIVATION:
            return "The user is feeling motivated. Be encouraging and energetic."

        if emotion == Emotion.DISAPPOINTMENT:
            return (
                "The user is disappointed. Acknowledge what didn't work out. "
                "Be compassionate."
            )

        if emotion in (Emotion.AFFECTION, Emotion.GRATITUDE):
            return (
                "The user is expressing warmth. Respond warmly without "
                "pretending to have human feelings."
            )

        return ""

    # ------------------------------------------------------------------

    def format_for_prompt(self, context: EmotionalContext) -> str:
        """
        Return a one-line string to prepend to the LLM system prompt, or an
        empty string when the emotional signal is too weak to be actionable.
        """
        if context.primary_emotion == Emotion.NEUTRAL or context.confidence < 0.3:
            return ""

        return (
            f"EMOTIONAL CONTEXT: The user appears to be feeling "
            f"{context.primary_emotion.value} "
            f"({context.intensity.value} intensity). "
            f"{context.response_approach}"
        )

    # ------------------------------------------------------------------

    def should_store_emotional_memory(
        self,
        context: EmotionalContext,
        message: str,
    ) -> bool:
        """
        Return True when this emotional moment is significant enough to persist
        as a long-term memory entry.

        A minimum message length of 20 characters is required so we don't
        store trivial one-word outbursts.
        """
        return context.store_as_memory and len(message) > 20

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _keyword_analysis(self, text: str) -> dict[Emotion, float]:
        """
        Count how many distinct patterns from EMOTION_PATTERNS appear in
        *text* (which should already be lowercased by the caller).

        Returns a dict of Emotion → raw match count.  NEUTRAL always gets 0.
        """
        scores: dict[Emotion, float] = {emotion: 0.0 for emotion in Emotion}

        for emotion, patterns in EMOTION_PATTERNS.items():
            if not patterns:
                # NEUTRAL — no patterns to check
                continue
            count = sum(1 for pattern in patterns if pattern in text)
            scores[emotion] = float(count)

        return scores

    def _normalize_scores(self, scores: dict[Emotion, float]) -> dict[Emotion, float]:
        """
        Divide all scores by the maximum score so the dominant emotion has a
        normalised value of 1.0.  Returns all-zeros if no signal was found.
        """
        max_score = max(scores.values(), default=0.0)
        if max_score == 0.0:
            return dict(scores)  # shallow copy, all zeros

        return {emotion: score / max_score for emotion, score in scores.items()}

    def _history_analysis(
        self,
        conversation_history: list[dict],
    ) -> dict[Emotion, float]:
        """
        Run keyword analysis over the last 3 *user* turns in
        *conversation_history* and return averaged raw scores.

        Each history item is expected to be ``{"role": "user"|"assistant",
        "content": "..."}``.  Non-user turns are skipped.
        """
        # Collect user messages in reverse chronological order, take up to 3
        user_texts: list[str] = []
        for turn in reversed(conversation_history):
            if turn.get("role") == "user" and isinstance(turn.get("content"), str):
                user_texts.append(turn["content"].lower())
                if len(user_texts) == 3:
                    break

        if not user_texts:
            return {emotion: 0.0 for emotion in Emotion}

        # Average the raw counts across the collected turns
        accumulated: dict[Emotion, float] = {emotion: 0.0 for emotion in Emotion}
        for text in user_texts:
            turn_scores = self._keyword_analysis(text)
            for emotion, score in turn_scores.items():
                accumulated[emotion] += score

        n = float(len(user_texts))
        return {emotion: total / n for emotion, total in accumulated.items()}

    # ------------------------------------------------------------------

    def _neutral_context(self, reason: str) -> EmotionalContext:
        """Convenience constructor for a fully neutral EmotionalContext."""
        return EmotionalContext(
            primary_emotion=Emotion.NEUTRAL,
            confidence=0.0,
            intensity=EmotionalIntensity.LOW,
            secondary_emotions=[],
            relevant_context=reason,
            response_approach="",
            should_acknowledge=False,
            store_as_memory=False,
        )


# ---------------------------------------------------------------------------
# Module-level singleton (mirrors the pattern used by other services)
# ---------------------------------------------------------------------------

emotional_intelligence_service = EmotionalIntelligenceService()
