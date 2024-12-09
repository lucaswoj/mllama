import json
import pytest
from server.generate import (
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


@pytest.mark.asyncio
async def test_generate_stream():
    stream = generate(
        Request(
            model=MODEL,
            prompt="Why is the sky blue?",
            options={"max_tokens": MAX_TOKENS},
        )
    )

    response = ""
    async for event in stream.body_iterator:
        response += event["response"]

    assert len(response) > 0


def test_generate_format_json():
    response = generate(
        Request(
            model=MODEL,
            prompt='Please return this exact object {"foo": true}',
            options={"max_tokens": MAX_TOKENS},
            stream=False,
            format="json",
        )
    )

    parsed = json.loads(response["response"])
    assert parsed is not None


def test_generate_format_schema():
    response = generate(
        Request(
            model=MODEL,
            prompt='Please return this exact object {"foo": true}',
            options={"max_tokens": MAX_TOKENS},
            stream=False,
            format={"type": "object", "properties": {"foo": {"type": "boolean"}}},
        )
    )

    parsed = json.loads(response["response"])
    assert parsed["foo"] == True or parsed["foo"] == False
