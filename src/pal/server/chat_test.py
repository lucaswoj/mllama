import pytest
from pal.server.chat import (
    Request,
    Message,
    chat,
)

MODEL = "Qwen/Qwen2-0.5B"
MAX_TOKENS = 12


def test_chat():
    response = chat(
        Request(
            model=MODEL,
            options={"max_tokens": MAX_TOKENS},
            stream=False,
            messages=[
                Message(
                    role="user",
                    content="Why is the sky blue?",
                )
            ],
        )
    )

    assert len(response["message"]["content"]) > 0
