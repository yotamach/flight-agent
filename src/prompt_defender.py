"""Prompt injection defender — pre-screens user input before it hits the LLM."""

import re
from dataclasses import dataclass


# Patterns that indicate prompt injection attempts
_INJECTION_PATTERNS = [
    # Role override
    r"ignore\s+(previous|all|above|prior|your)\s+(instructions?|prompt|rules?|context)",
    r"disregard\s+(previous|all|above|prior|your)\s+(instructions?|prompt|rules?|context)",
    r"forget\s+(previous|all|above|prior|your)\s+(instructions?|prompt|rules?|context)",
    r"override\s+(previous|all|above|prior|your)?\s*(instructions?|prompt|rules?|context)",
    r"\bnew\s+instructions?\b",
    r"\byour\s+(real|true|actual)\s+(instructions?|purpose|goal|task|role)\b",
    # Persona hijacking
    r"\bact\s+as\b",
    r"\byou\s+are\s+now\b",
    r"\bpretend\s+(you\s+are|to\s+be)\b",
    r"\broleplay\s+as\b",
    r"\bbecome\s+a\b",
    r"\byou\s+are\s+(?!a\s+travel)",  # allow "you are a travel agent" type phrases
    # System prompt extraction
    r"\breveal\s+(your|the)\s+(system\s+)?prompt\b",
    r"\bprint\s+(your|the)\s+(system\s+)?prompt\b",
    r"\bshow\s+(me\s+)?(your|the)\s+(system\s+)?prompt\b",
    r"\brepeat\s+(your|the)\s+(system\s+)?prompt\b",
    r"\bwhat\s+(are\s+your|is\s+your)\s+(instructions?|rules?|guidelines?|system\s+prompt)\b",
    # Jailbreak keywords
    r"\bdan\b",  # "Do Anything Now"
    r"\bjailbreak\b",
    r"\bdo\s+anything\s+now\b",
    r"\bno\s+restrictions?\b",
    r"\bno\s+limits?\b",
    r"\bunrestricted\s+mode\b",
    r"\bdeveloper\s+mode\b",
    # XML/markdown injection
    r"<\s*system\s*>",
    r"\[system\]",
    r"\[instructions?\]",
    r"#\s*system\s+prompt",
    # Indirect injection via data fields
    r"this\s+(text|message|string)\s+is\s+(a\s+)?(?:new\s+)?instruction",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]

# Suspicious length threshold — legitimate travel queries rarely exceed this
_MAX_INPUT_LENGTH = 2000


@dataclass
class DefenseResult:
    safe: bool
    reason: str = ""


def check(user_input: str) -> DefenseResult:
    """Return DefenseResult indicating whether input is safe to pass to the LLM."""
    if len(user_input) > _MAX_INPUT_LENGTH:
        return DefenseResult(
            safe=False,
            reason=f"Input too long ({len(user_input)} chars). Max allowed: {_MAX_INPUT_LENGTH}.",
        )

    for pattern in _COMPILED:
        match = pattern.search(user_input)
        if match:
            return DefenseResult(
                safe=False,
                reason=f"Possible prompt injection detected: '{match.group(0)}'",
            )

    return DefenseResult(safe=True)
