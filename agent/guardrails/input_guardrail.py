"""
SceneForge AI - Input Guardrail
Filters prompt injections, malicious commands, and unsupported complex operations.
"""

from typing import Tuple
from shared.constants import GUARDRAILS

def validate_user_prompt(prompt: str) -> Tuple[bool, str]:
    """
    Validates natural language input against security constraints.
    Returns (is_valid, reason_or_message).
    """
    if not prompt or len(prompt.strip()) < 3:
        return False, "Prompt is too short to extract geometric intent."

    if len(prompt) > 2000:
        return False, "Prompt exceeds maximum allowed length (2000 characters)."

    lower_prompt = prompt.lower()
    for pattern in GUARDRAILS["DISALLOWED_PYTHON_PATTERNS"]:
        if pattern in lower_prompt:
            return False, f"Prompt contains prohibited code execution token: '{pattern}'"

    return True, "Prompt passed security guardrail verification."
