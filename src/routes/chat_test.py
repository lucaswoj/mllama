import pytest
from routes.chat import chat


# @pytest.mark.asyncio
def test_plain():
    result = chat("Hello")
    assert result is not None  # Add your assertions here
