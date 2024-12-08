import pytest
from entrypoints.server import GenerateRequest, generate


model = "/Users/lucaswoj/.cache/huggingface/hub/models--Qwen--Qwen2-0.5B/snapshots/91d2aff3f957f99e4c74c962f2f408dcc88a18d8"


@pytest.mark.asyncio
async def test_generate_stream():
    stream = generate(
        GenerateRequest(
            model=model, prompt="Why is the sky blue?", options={"max_tokens": 12}
        )
    )

    response = ""
    async for response_chunk in stream.body_iterator:
        response += response_chunk.response

    assert response is not None


def test_generate_no_stream():
    response = generate(
        GenerateRequest(
            model=model,
            prompt="Why is the sky blue?",
            options={"max_tokens": 12},
            stream=False,
        )
    )

    assert response.response is not None
