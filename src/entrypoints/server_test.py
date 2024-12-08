import json
import pytest
from entrypoints.server import GenerateRequest, generate


model = "/Users/lucaswoj/.cache/huggingface/hub/models--Qwen--Qwen2-0.5B/snapshots/91d2aff3f957f99e4c74c962f2f408dcc88a18d8"
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
