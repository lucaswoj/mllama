from type.ToolCall import ToolCall
from pydantic import BaseModel
from typing import List, Literal, Optional


class Message(BaseModel):
    # the role of the message, either system, user, assistant, or tool
    role: Literal["system", "user", "assistant", "tool"]
    # the content of the message
    content: str
    # a list of images to include in the message (for multimodal models such as llava)
    images: Optional[List[str]] = None
    # a list of tools the model wants to use
    tool_calls: Optional[List[ToolCall]] = None
