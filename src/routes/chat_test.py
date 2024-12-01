import pytest
from routes.chat import chat


@pytest.mark.asyncio
async def test_not_streaming():
    result = await chat("Hello")
    assert result is not None  # Add your assertions here


@pytest.mark.asyncio
async def test_treaming():
    result = await chat("Hello", stream=True)
    assert result is not None  # Add your assertions here
