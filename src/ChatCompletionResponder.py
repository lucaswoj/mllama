import time


class ChatCompletionResponder:
    def __init__(self, model_name: str):
        self.object_type = "chat.completion"
        self.model_name = model_name
        self.created = int(time.time())
        self.id = f"{id(self)}_{self.created}"
        self.content = ""

    def message_properties(self):
        return {
            "object": self.object_type,
            "id": f"chatcmpl-{self.id}",
            "created": self.created,
            "model": self.model_name,
        }

    def translate_reason(self, reason):
        """
        Translate our reason codes to OpenAI ones.
        """
        if reason == "end":
            return "stop"
        if reason == "max_tokens":
            return "length"
        return f"error: {reason}"  # Not a standard OpenAI API reason

    def format_usage(self, prompt_tokens: int, completion_tokens: int):
        return {
            "usage": {
                "completion_tokens": completion_tokens,
                "prompt_tokens": prompt_tokens,
                "total_tokens": completion_tokens + prompt_tokens,
            },
        }

    def generated_tokens(
        self,
        text: str,
    ):
        self.content += text
        return None

    def generation_stopped(
        self,
        stop_reason: str,
        prompt_tokens: int,
        completion_tokens: int,
    ):
        finish_reason = self.translate_reason(stop_reason)
        message = {"role": "assistant", "content": self.content}
        return {
            "choices": [
                {"index": 0, "message": message, "finish_reason": finish_reason}
            ],
            **self.format_usage(prompt_tokens, completion_tokens),
            **self.message_properties(),
        }
