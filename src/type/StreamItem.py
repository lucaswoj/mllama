from typing import List, Optional
from pydantic import BaseModel


class StreamItem(BaseModel):
    # the model used for generating the response
    model: str
    # the timestamp when the response was created
    created_at: str
    # the content of the streaming message
    response: str
    # a flag indicating if the message is the final part of the stream
    done: bool
    # total time spent generating the response
    total_duration: Optional[int] = None
    # time spent in nanoseconds loading the model
    load_duration: Optional[int] = None
    # number of tokens in the prompt
    prompt_eval_count: Optional[int] = None
    # time spent in nanoseconds evaluating the prompt
    prompt_eval_duration: Optional[int] = None
    # number of tokens in the response
    eval_count: Optional[int] = None
    # time in nanoseconds spent generating the response
    eval_duration: Optional[int] = None
    # an encoding of the conversation used in this response
    context: Optional[List[int]] = None
