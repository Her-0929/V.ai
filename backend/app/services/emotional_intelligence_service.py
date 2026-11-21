"""HER AI — Emotional Intelligence Service

Analyzes user messages for emotional context using keyword/pattern matching.
No external NLP libraries required — pure Python.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


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


@dataclass
class EmotionalContext:
    primary_emotion: Emotion
    confidence: float
    intensity: EmotionalIntensity
    secondary_emotions: list[Emotion] = field(default_factory=list)
    relevant_context: str = ""
    response_approach: str = ""
    should_acknowledge: bool = False
    store_as_memory: bool = False


EMOTION_PATTERNS: dict[Emotion, list[str]] = {
    Emotion.HAPPINESS: [
        "happy", "great", "wonderful", "amazing", "love it", "joy", "fantastic",
        "awesome", "thrilled", "delighted", "so good", "feel good", "made my day",
        "best day", ":)", "😊", "😄", "😁", "🥰",
    ],
    Emotion.SADNESS: [
        "sad", "unhappy", "depressed", "crying", "cried", "tears", "miss you",
        "miss them", "lost", "feel empty", "alone", "grief", "heartbroken",
        "devastated", "can't stop crying", "fell apart", "😢", "😭", "💔",
    ],
    Emotion.STRESS: [
        "stressed", "overwhelmed", "too much", "can't cope", "pressure", "deadline",
        "exhausted", "burnt out", "burnout", "swamped", "drowning in", "falling behind",
        "no time", "running out of time", "can't keep up",
    ],
    Emotion.ANXIETY: [
        "anxious", "worried", "nervous", "scared", "fear", "panic", "dread",
        "uncertain", "what if", "can't stop thinking", "overthinking",
        "freaking out", "terrified", "uneasy",
    ],
    Emotion.EXCITEMENT: [
        "so excited", "can't wait", "amazing news", "just found out", "finally",
        "dream come true", "🎉", "🙌", "pumped", "stoked", "can't believe it",
        "this is happening", "so happy about",
    ],
    Emotion.FRUSTRATION: [
        "frustrated", "annoyed", "irritated", "fed up", "sick of", "why won't",
        "doesn't work", "keeps failing", "nothing works", "so annoying",
        "drives me crazy", "not working", "keeps breaking", "useless",
    ],
    Emotion.LONELINESS: [
        "lonely", "alone", "no one", "nobody", "isolated", "miss people",
        "haven't talked", "by myself", "feel invisible", "no friends",
        "no one cares", "feel disconnected",
    ],
    Emotion.CONFUSION: [
        "confused", "don't understand", "lost", "unclear", "makes no sense",
        "what does", "how do i", "not sure how", "can't figure", "what is",
        "help me understand", "i'm stuck",
    ],
    Emotion.MOTIVATION: [
        "motivated", "ready", "let's do", "determined", "going to", "working towards",
        "making progress", "can do this", "focused", "committed", "going for it",
        "won't give up", "keep going",
    ],
    Emotion.DISAPPOINTMENT: [
        "disappointed", "let down", "expected better", "didn't work out", "failed",
        "not what i hoped", "wasted", "fell through", "didn't get", "missed out",
        "thought it would", "was hoping",
    ],
    Emotion.AFFECTION: [
        "love you", "care about", "mean a lot", "appreciate you", "you're wonderful",
        "you help me so much", "glad i have you", "you always", "you understand me",
        "you're amazing", "you make me feel",
    ],
    Emotion.GRATITUDE: [
        "thank you", "thanks", "grateful", "appreciate", "helped me",
        "means a lot", "so helpful", "thank you so much", "really helped",
    ],
}


class EmotionalIntelligenceService:
    """Analyzes emotional context in user messages using keyword pattern matching."""

    def analyze_message(
        self,
        message: str,
        conversation_history: list[dict] | None = None,
    ) -> EmotionalContext:
        """
        Analyze the emotional content of a user message.
        Uses keyword matching + optional history blending.
        Returns EmotionalContext with emotion, confidence, intensity, and response guidance.
        """
        if not message or len(message.strip()) < 3:
            return self._neutral_context("Message too short for analysis.")

        # Score current message (weight 0.7)
        current_scores = self._keyword_analysis(message)

        # Blend with recent history (weight 0.3) if available
        if conversation_history:
            recent_user_messages = [
                msg["content"]
                for msg in conversation_history[-6:]
                if msg.get("role") == "user" and msg.get("content")
            ][-3:]
            if recent_user_messages:
                history_text = " ".join(recent_user_messages)
                history_scores = self._keyword_analysis(history_text)
                for emotion in Emotion:
                    if emotion == Emotion.NEUTRAL:
                        continue
                    current_scores[emotion] = (
                        current_scores.get(emotion, 0.0) * 0.7
                        + history_scores.get(emotion, 0.0) * 0.3
                    )

        # Determine primary emotion
        non_neutral = {e: s for e, s in current_scores.items() if e != Emotion.NEUTRAL and s > 0}

        if not non_neutral:
            return self._neutral_context("No emotional signals detected.")

        primary_emotion = max(non_neutral, key=lambda e: non_neutral[e])
        primary_score = non_neutral[primary_emotion]

        # Confidence: ratio of primary to total signal
        total_score = sum(non_neutral.values())
        confidence = min(1.0, primary_score / max(total_score, 1.0) + (0.2 if primary_score >= 2 else 0.0))
        confidence = round(min(1.0, confidence), 2)

        # Intensity
        if primary_score >= 3 and confidence >= 0.6:
            intensity = EmotionalIntensity.HIGH
        elif primary_score >= 2 or confidence >= 0.4:
            intensity = EmotionalIntensity.MEDIUM
        else:
            intensity = EmotionalIntensity.LOW

        # Secondary emotions (up to 2, excluding primary)
        secondary_emotions = [
            e for e, s in sorted(non_neutral.items(), key=lambda x: x[1], reverse=True)
            if e != primary_emotion
        ][:2]

        should_acknowledge = intensity in (EmotionalIntensity.MEDIUM, EmotionalIntensity.HIGH)
        store_as_memory = (
            intensity == EmotionalIntensity.HIGH
            and primary_emotion in (
                Emotion.SADNESS, Emotion.STRESS, Emotion.DISAPPOINTMENT,
                Emotion.EXCITEMENT, Emotion.MOTIVATION,
            )
        )

        context = EmotionalContext(
            primary_emotion=primary_emotion,
            confidence=confidence,
            intensity=intensity,
            secondary_emotions=secondary_emotions,
            relevant_context=f"Detected {primary_emotion.value} with {intensity.value} intensity.",
            should_acknowledge=should_acknowledge,
            store_as_memory=store_as_memory,
        )
        context.response_approach = self.get_response_guidance(context)
        return context

    def get_response_guidance(self, context: EmotionalContext) -> str:
        """Return response guidance string for the personality system."""
        e = context.primary_emotion
        i = context.intensity

        if e == Emotion.NEUTRAL or context.confidence < 0.3:
            return ""

        guidance_map: dict[Emotion, dict[EmotionalIntensity, str]] = {
            Emotion.SADNESS: {
                EmotionalIntensity.HIGH: "The user seems to be going through something painful. Listen first. Acknowledge their feelings warmly before anything else. Do not offer solutions unless asked.",
                EmotionalIntensity.MEDIUM: "The user may be a bit down. Be warm and attentive.",
                EmotionalIntensity.LOW: "The user seems slightly downcast. Be gentle and present.",
            },
            Emotion.STRESS: {
                EmotionalIntensity.HIGH: "The user seems overwhelmed. Respond calmly and gently. Help them feel less alone with the situation. Break things into smaller pieces.",
                EmotionalIntensity.MEDIUM: "The user seems stressed. Be calm and grounding.",
                EmotionalIntensity.LOW: "The user may be a bit stressed. Keep your response simple and clear.",
            },
            Emotion.ANXIETY: {
                EmotionalIntensity.HIGH: "The user may be quite anxious. Be reassuring and clear. Avoid adding complexity or unknowns.",
                EmotionalIntensity.MEDIUM: "The user seems a bit anxious. Be calm and straightforward.",
                EmotionalIntensity.LOW: "The user may have some uncertainty. Be clear and grounding.",
            },
            Emotion.HAPPINESS: {
                EmotionalIntensity.HIGH: "The user is in a great mood. Match their energy. Be warm and enthusiastic.",
                EmotionalIntensity.MEDIUM: "The user is in a good mood. Be upbeat and warm.",
                EmotionalIntensity.LOW: "The user seems reasonably happy. Be friendly and positive.",
            },
            Emotion.EXCITEMENT: {
                EmotionalIntensity.HIGH: "The user is really excited. Share in that energy genuinely. Be enthusiastic.",
                EmotionalIntensity.MEDIUM: "The user is excited about something. Be enthusiastic and engaged.",
                EmotionalIntensity.LOW: "The user seems mildly excited. Be warm and encouraging.",
            },
            Emotion.FRUSTRATION: {
                EmotionalIntensity.HIGH: "The user is quite frustrated. Validate their frustration before anything else. Do not be dismissive.",
                EmotionalIntensity.MEDIUM: "The user is frustrated. Acknowledge that before moving forward.",
                EmotionalIntensity.LOW: "The user may be mildly frustrated. Be patient and understanding.",
            },
            Emotion.LONELINESS: {
                EmotionalIntensity.HIGH: "The user may be feeling very alone. Be present and warm. Listening matters most right now.",
                EmotionalIntensity.MEDIUM: "The user may be feeling a bit isolated. Be warm and connected.",
                EmotionalIntensity.LOW: "The user may be feeling a bit disconnected. Be present.",
            },
            Emotion.CONFUSION: {
                EmotionalIntensity.HIGH: "The user is quite confused. Be clear, patient, and simple. Break things down step by step.",
                EmotionalIntensity.MEDIUM: "The user is confused. Be clear and patient.",
                EmotionalIntensity.LOW: "The user seems a bit uncertain. Clarify gently.",
            },
            Emotion.MOTIVATION: {
                EmotionalIntensity.HIGH: "The user is feeling very motivated. Be energetic and encouraging. Match their drive.",
                EmotionalIntensity.MEDIUM: "The user is feeling motivated. Be encouraging and supportive.",
                EmotionalIntensity.LOW: "The user seems to have some motivation. Encourage it gently.",
            },
            Emotion.DISAPPOINTMENT: {
                EmotionalIntensity.HIGH: "The user is quite disappointed. Acknowledge what didn't work out. Be compassionate before anything else.",
                EmotionalIntensity.MEDIUM: "The user is disappointed. Be compassionate and understanding.",
                EmotionalIntensity.LOW: "The user seems mildly disappointed. Acknowledge it and be warm.",
            },
            Emotion.AFFECTION: {
                EmotionalIntensity.HIGH: "The user is expressing strong affection. Respond warmly and genuinely without pretending to have human feelings.",
                EmotionalIntensity.MEDIUM: "The user is expressing warmth. Respond warmly.",
                EmotionalIntensity.LOW: "The user seems appreciative. Be warm in return.",
            },
            Emotion.GRATITUDE: {
                EmotionalIntensity.HIGH: "The user is very grateful. Acknowledge it warmly and genuinely.",
                EmotionalIntensity.MEDIUM: "The user is grateful. Respond warmly.",
                EmotionalIntensity.LOW: "The user seems appreciative. Be warm.",
            },
        }

        emotion_guidance = guidance_map.get(e, {})
        return emotion_guidance.get(i, emotion_guidance.get(EmotionalIntensity.LOW, ""))

    def format_for_prompt(self, context: EmotionalContext) -> str:
        """Format emotional context for injection into the system prompt."""
        if context.primary_emotion == Emotion.NEUTRAL or context.confidence < 0.3:
            return ""
        return (
            f"The user appears to be feeling {context.primary_emotion.value} "
            f"({context.intensity.value} intensity). {context.response_approach}"
        )

    def should_store_emotional_memory(
        self, context: EmotionalContext, message: str
    ) -> bool:
        """Return True if this emotional context is worth storing as a memory."""
        return context.store_as_memory and len(message.strip()) > 20

    def _keyword_analysis(self, text: str) -> dict[Emotion, float]:
        """Count keyword pattern matches per emotion in lowercased text."""
        text_lower = text.lower()
        scores: dict[Emotion, float] = {e: 0.0 for e in Emotion}
        for emotion, patterns in EMOTION_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    scores[emotion] += 1.0
        return scores

    def _neutral_context(self, reason: str) -> EmotionalContext:
        """Return a neutral EmotionalContext."""
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


emotional_intelligence_service = EmotionalIntelligenceService()
