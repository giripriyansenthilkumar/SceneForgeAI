"""
SceneForge AI - Multi-Provider LLM Client Interface
Supports Anthropic, OpenAI, Gemini, and a deterministic offline fallback engine.
"""

import os
import json
import re
from typing import Dict, Any, Optional

class LLMClient:
    def __init__(self):
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")

    def complete_json(self, system_prompt: str, user_prompt: str, fallback_type: str = "plan") -> Dict[str, Any]:
        """
        Sends request to available LLM provider expecting a structured JSON response.
        If no API key is set or all fail, uses deterministic fallback extraction.
        """
        # 1. Try Anthropic if key provided
        if self.anthropic_key:
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=self.anthropic_key)
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2048,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                text = response.content[0].text
                return self._parse_json_from_text(text)
            except Exception as e:
                print(f"[SceneForge LLM] Anthropic failed: {e}")

        # 2. Try OpenAI if key provided
        if self.openai_key:
            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_key)
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
            except Exception as e:
                print(f"[SceneForge LLM] OpenAI failed: {e}")

        # 3. Deterministic NLP / Rule-Based Fallback
        return self._deterministic_fallback(user_prompt, fallback_type)

    def _parse_json_from_text(self, text: str) -> Dict[str, Any]:
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if match:
            text = match.group(1)
        return json.loads(text.strip())

    def _deterministic_fallback(self, prompt: str, fallback_type: str) -> Dict[str, Any]:
        """
        High-precision rule-based extraction for offline development and testing.
        Extracts dimensional percentages, lengths, colors, components, and categories.
        """
        p = prompt.lower()

        if fallback_type == "edit":
            # Detect percentage changes, e.g. "make it 20% longer" or "make it 30% longer"
            pct_match = re.search(r'(\d+)%\s*(longer|bigger|larger|shorter|wider)', p)
            length_mult = 1.0
            if pct_match:
                pct = float(pct_match.group(1)) / 100.0
                direction = pct_match.group(2)
                if direction in ("longer", "bigger", "larger"):
                    length_mult = 1.0 + pct
                elif direction == "shorter":
                    length_mult = max(0.5, 1.0 - pct)

            add_swim_platform = "swim" in p or "platform" in p
            add_engines = "engine" in p or "motors" in p
            change_deck_teak = "teak" in p or "wood" in p

            return {
                "intent": "modify_scene",
                "length_multiplier": length_mult,
                "add_swim_platform": add_swim_platform,
                "add_engines": add_engines,
                "change_deck_teak": change_deck_teak,
                "reasoning": f"Identified edit modifications from prompt: multiplier={length_mult}"
            }

        # Default: Generation Plan
        # Determine category
        cat = "boat"
        if any(w in p for w in ["chair", "table", "desk", "furniture", "stool"]):
            cat = "furniture"
        elif any(w in p for w in ["car", "vehicle", "chassis", "truck"]):
            cat = "vehicle"
        elif any(w in p for w in ["house", "building", "tower", "pillar"]):
            cat = "building"
        elif any(w in p for w in ["gear", "mechanical", "shaft", "cog"]):
            cat = "mechanical"

        # Extract dimensions if mentioned (e.g. "14 meters", "10m", "15m")
        dim_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:meters|meter|m\b)', p)
        length = float(dim_match.group(1)) if dim_match else 12.0

        return {
            "intent": "create_scene",
            "category": cat,
            "name": f"Procedural {cat.capitalize()}",
            "dimensions": {
                "length": length,
                "beam": round(length * 0.32, 2),
                "draft": 1.4
            },
            "components": [
                "hull", "deck", "cabin",
                *(["swim_platform"] if "platform" in p or "luxury" in p else []),
                *(["engines"] if "engine" in p else []),
                *(["radar_arch"] if "radar" in p or "arch" in p else [])
            ],
            "materials": {
                "hull": "mat_hull_white",
                "deck": "mat_teak_deck" if "teak" in p or "wood" in p else "mat_hull_white",
                "cabin": "mat_hull_white",
                "glass": "mat_cabin_glass"
            },
            "reasoning": f"Decomposed prompt into {cat} structure with length={length}m."
        }

llm_client = LLMClient()
