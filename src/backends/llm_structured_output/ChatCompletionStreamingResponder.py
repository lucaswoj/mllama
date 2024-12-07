from typing import Any, Optional
from chat.ChatCompletionResponder import ChatCompletionResponder


import json


class ChatCompletionStreamingResponder(ChatCompletionResponder):
    def __init__(self, model_name: str, schema: Optional[dict] = None, _model=None):
        super().__init__(model_name)
        self.object_type = "chat.completion.chunk"
        if schema:
            assert _model
            self.schema_parser = _model.get_driver_for_json_schema(schema)
        else:
            self.schema_parser = None

    def generated_tokens(
        self,
        text: str,
    ):
        delta: dict[str, Any] = {"role": "assistant", "content": text}
        if self.schema_parser:
            values: dict[str, str] = {}
            for char in text:
                self.schema_parser.advance_char(char)
                for path in self.schema_parser.get_current_value_paths():
                    values[path] = values.get(path, "") + char
            delta["values"] = values
        message = {
            "choices": [{"index": 0, "delta": delta, "finish_reason": None}],
            **self.message_properties(),
        }
        return f"data: {json.dumps(message)}\n"

    def generation_stopped(
        self,
        stop_reason: str,
        prompt_tokens: int,
        completion_tokens: int,
    ):
        finish_reason = self.translate_reason(stop_reason)
        delta = {"role": "assistant", "content": ""}
        message = {
            "choices": [{"index": 0, "delta": delta, "finish_reason": finish_reason}],
            # Usage field notes:
            # - OpenAI only sends usage in streaming if the option
            #   stream_options.include_usage is true, but we send it always.
            **self.format_usage(prompt_tokens, completion_tokens),
            **self.message_properties(),
        }
        return f"data: {json.dumps(message)}\ndata: [DONE]\n"
