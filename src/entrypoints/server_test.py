import json
import pytest
from entrypoints.server import GenerateRequest, generate


model = "Qwen/Qwen2-0.5B"
MAX_TOKENS = 12


def test_generate():
    response = generate(
        GenerateRequest(
            model=model,
            prompt="Why is the sky blue?",
            options={"max_tokens": MAX_TOKENS},
            stream=False,
        )
    )

    assert len(response.response) > 0


@pytest.mark.asyncio
async def test_generate_stream():
    stream = generate(
        GenerateRequest(
            model=model,
            prompt="Why is the sky blue?",
            options={"max_tokens": MAX_TOKENS},
        )
    )

    response = ""
    async for response_chunk in stream.body_iterator:
        response += response_chunk.response

    assert len(response) > 0


def test_generate_format_json():
    response = generate(
        GenerateRequest(
            model=model,
            prompt='Please return this exact object {"foo": true}',
            options={"max_tokens": MAX_TOKENS},
            stream=False,
            format="json",
        )
    )

    print(response.response)
    parsed = json.loads(response.response)
    assert parsed is not None


def test_generate_format_schema():
    response = generate(
        GenerateRequest(
            model=model,
            prompt='Please return this exact object {"foo": true}',
            options={"max_tokens": MAX_TOKENS},
            stream=False,
            format={"type": "object", "properties": {"foo": {"type": "boolean"}}},
        )
    )

    print(response.response)
    parsed = json.loads(response.response)
    assert parsed["foo"] is not None
