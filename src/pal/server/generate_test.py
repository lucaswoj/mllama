import json
import pytest
from pal.server.generate import (
    Request,
    generate,
)


MODEL = "Qwen/Qwen2-0.5B"
MAX_TOKENS = 12


def test_generate_basic():
    response = generate(
        Request(
            model=MODEL,
            prompt="Why is the sky blue?",
            options={"max_tokens": MAX_TOKENS},
            stream=False,
        )
    )

    assert len(response["response"]) > 0


def test_generate_format_schema():
    response = generate(
        Request(
            model=MODEL,
            prompt='Output a json object with the form {"foo": boolean}',
            options={"max_tokens": MAX_TOKENS},
            stream=False,
            format={"type": "object", "properties": {"foo": {"type": "boolean"}}},
        )
    )

    parsed = json.loads(response["response"])
    assert parsed["foo"] == True or parsed["foo"] == False
