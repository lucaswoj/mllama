from pal.main import app
import pytest
from pal.routers.chat import (
    Request,
    Message,
    chat,
)
from fastapi.testclient import TestClient
import json

MODEL = "Qwen/Qwen2-0.5B"
MAX_TOKENS = 12
CLIENT = TestClient(app)


def test_chat_simple():
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


def test_chat_stream():
    CLIENT.post(
        "/api/chat",
        json=Request(
            model=MODEL,
            options={"max_tokens": MAX_TOKENS},
            stream=True,
            messages=[
                Message(
                    role="user",
                    content="Why is the sky blue?",
                )
            ],
        ).model_dump(),
    )


def test_chat_schema():
    response = CLIENT.post(
        "/api/chat",
        json=Request(
            model=MODEL,
            options={"max_tokens": MAX_TOKENS},
            stream=False,
            format={"type": "object", "properties": {"foo": {"type": "boolean"}}},
            messages=[
                Message(
                    role="user",
                    content='Output a json object with the form {"foo": boolean}',
                )
            ],
        ).model_dump(),
    ).json()

    parsed = json.loads(response["message"]["content"])
    assert parsed["foo"] == True or parsed["foo"] == False
