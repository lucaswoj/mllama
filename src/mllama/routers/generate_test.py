import json
from fastapi.testclient import TestClient
from mllama.main import app
import fastapi
from mllama.routers.generate import (
    Params,
)


MODEL = "Qwen/Qwen2-0.5B"
MAX_TOKENS = 12
FASTAPI_REQUEST = fastapi.Request(
    {"type": "http", "http_version": "1.1", "method": "POST", "scheme": "http"}
)
CLIENT = TestClient(app)


def test_simple():
    response = CLIENT.post(
        "/api/generate",
        json=Params(
            model=MODEL,
            prompt="Why is the sky blue?",
            options={"max_tokens": MAX_TOKENS},
            stream=False,
        ).model_dump(),
    ).json()

    assert len(response["response"]) > 0


def test_stream():
    CLIENT.post(
        "/api/generate",
        json=Params(
            model=MODEL,
            prompt="Why is the sky blue?",
            options={"max_tokens": MAX_TOKENS},
            stream=True,
        ).model_dump(),
    )


def test_schema():
    response = CLIENT.post(
        "/api/generate",
        json=Params(
            model=MODEL,
            prompt='Output a json object with the form {"foo": boolean}',
            options={"max_tokens": MAX_TOKENS},
            stream=False,
            format={"type": "object", "properties": {"foo": {"type": "boolean"}}},
        ).model_dump(),
    ).json()

    parsed = json.loads(response["response"])
    assert parsed["foo"] == True or parsed["foo"] == False
