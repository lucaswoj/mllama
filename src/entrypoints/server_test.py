import pytest
from entrypoints.server import GenerateRequest, generate


model = "Qwen/Qwen2-0.5B"


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
