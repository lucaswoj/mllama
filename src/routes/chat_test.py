import pytest
from routes.chat import chat


# @pytest.mark.asyncio
def test_simple():
    result = chat("Hello")
    assert result is not None


# @pytest.mark.asyncio
def test_json():
    result = chat("Hello", format="json")
    assert result is not None


# @pytest.mark.asyncio
def test_stream():
    result = chat("Hello", stream=True)
    assert result is not None
