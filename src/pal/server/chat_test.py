import fastapi
from pal.server.server import server
import pytest
from pal.server.chat import (
    Request,
    Message,
    chat,
)
from fastapi.testclient import TestClient

MODEL = "Qwen/Qwen2-0.5B"
MAX_TOKENS = 12
CLIENT = TestClient(server)


@pytest.mark.asyncio
async def test_chat():
    response = CLIENT.post(
        "/api/chat",
        json=Request(
            model=MODEL,
            options={"max_tokens": MAX_TOKENS},
            stream=False,
            messages=[
                Message(
                    role="user",
                    content="Why is the sky blue?",
                )
            ],
        ).model_dump(),
    ).json()

    assert len(response["message"]["content"]) > 0
