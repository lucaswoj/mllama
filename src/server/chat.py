from typing import List, Literal, Optional
from pydantic import BaseModel
from typing import List, Optional, Literal
from typing import List, Literal, Optional
from mlx_lm import load, stream_generate
from pydantic import BaseModel
from server.base import server

from pydantic import BaseModel


class Message(BaseModel):
    # the role of the message, either system, user, assistant, or tool
    role: Literal["system", "user", "assistant", "tool"]
    # the content of the message
    content: str
    # a list of images to include in the message (for multimodal models such as llava)
    images: Optional[List[str]] = None
    # a list of tools the model wants to use
    tool_calls: Optional[List[dict]] = None

class ChatRequest(BaseModel):
    model: str = "mlx-community/Llama-3.2-3B-Instruct"
    messages: List[Message]
    tools: Optional[List[dict]] = None
    format: Optional[str] = None
    options: Optional[dict] = None
    stream: Optional[bool] = True
    keep_alive: Optional[str] = "5m"

@server.post("/api/chat")
async def chat(request: ChatRequest):
  """
  Generate the next message in a chat with a provided model.
  """

  messages = request.messages
  model = request.model

  if isinstance(messages, str):
    messages = [Message(role="user", content=messages)]

  if model.startswith("mlx-community/"):
      model_obj, tokenizer = load(model)
      prompt = tokenizer.apply_chat_template(
          messages, tokenize=False, add_generation_prompt=True
      )
      return stream_generate(model_obj, tokenizer, prompt, max_tokens=512)
  else:
      raise ValueError("Model name must start with 'mlx-community/'")
