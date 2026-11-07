"""Explicitly limited text-to-sensory encoder; NOT language comprehension."""

from __future__ import annotations

import hashlib
import re


class TextSensor:
    """Deterministic hashed bag of tokens, one channel per feature bin."""

    MAX_TEXT_LENGTH = 20_000

    def __init__(self, channels: int = 8) -> None:
        if type(channels) is not int or not 1 <= channels <= 4096:
            raise ValueError("channels must be in [1, 4096]")
        self.channels = channels

    def encode(self, text: str) -> list[float]:
        if not isinstance(text, str) or len(text) > self.MAX_TEXT_LENGTH:
            raise ValueError("text must be a string up to 20,000 characters")
        features = [0.0] * self.channels
        for token in re.findall(r"\w+", text.casefold(), flags=re.UNICODE):
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            slot = int.from_bytes(digest, "little") % self.channels
            features[slot] = min(1.0, features[slot] + 0.5)
        return features
