from typing import Any
from chat.V1Function import V1Function
from chat.ToolCallResponder import ToolCallResponder


import json


class ToolCallStreamingResponder(ToolCallResponder):
    def __init__(
        self,
        model_name: str,
        functions: list[V1Function],
        is_legacy_function_call: bool,
        _model,
    ):
        super().__init__(model_name, functions, is_legacy_function_call)
        self.object_type = "chat.completion.chunk"

        # We need to parse the output as it's being generated in order to send
        # streaming messages that contain the name and arguments of the function
        # being called.

        self.current_function_index = -1
        self.current_function_name = None
        self.in_function_arguments = False

        def set_function_name(_prop_name: str, prop_value):
            self.current_function_index += 1
            self.current_function_name = prop_value

        def start_function_arguments(_prop_name: str):
            self.in_function_arguments = True

        def end_function_arguments(_prop_name: str, _prop_value: str):
            self.in_function_arguments = False

        hooked_function_schemas = [
            {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "const",
                        "const": fn.name,
                        "__hooks": {
                            "value_end": set_function_name,
                        },
                    },
                    "arguments": {
                        **fn.parameters,
                        "__hooks": {
                            "value_start": start_function_arguments,
                            "value_end": end_function_arguments,
                        },
                    },
                },
                "required": ["name", "arguments"],
            }
            for fn in functions
        ]
        hooked_schema: dict[str, Any]
        if len(hooked_function_schemas) == 1:
            hooked_schema = hooked_function_schemas[0]
        elif is_legacy_function_call:
            hooked_schema = {"oneOf": hooked_function_schemas}
        else:
            hooked_schema = {
                "type": "array",
                "items": {"anyOf": hooked_function_schemas},
            }
        self.tool_call_parser = _model.get_driver_for_json_schema(hooked_schema)

    def generated_tokens(
        self,
        text: str,
    ):
        argument_text = ""
        for char in text:
            if self.in_function_arguments:
                argument_text += char
            # Update state. This is certain to parse, no need to check for rejections.
            self.tool_call_parser.advance_char(char)
        if not argument_text:
            return None
        assert self.current_function_name
        delta: dict[str, Any]
        if self.is_legacy_function_call:
            delta = {
                "function_call": {
                    "name": self.current_function_name,
                    "arguments": argument_text,
                }
            }
        else:
            delta = {
                "tool_calls": [
                    {
                        "index": self.current_function_index,
                        "id": f"call_{self.id}_{self.current_function_index}",
                        "type": "function",
                        "function": {
                            # We send the name on every update, but OpenAI only sends it on
                            # the first one for each call, with empty arguments (""). Further
                            # updates only have the arguments field. This is something we may
                            # want to emulate if client code depends on this behavior.
                            "name": self.current_function_name,
                            "arguments": argument_text,
                        },
                    }
                ]
            }
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
        message = {
            "choices": [{"index": 0, "delta": {}, "finish_reason": finish_reason}],
            # Usage field notes:
            # - OpenAI only sends usage in streaming if the option
            #   stream_options.include_usage is true, but we send it always.
            # - OpenAI sends two separate messages: one with the finish_reason and no
            #   usage field, and one with an empty choices array and the usage field.
            **self.format_usage(prompt_tokens, completion_tokens),
            **self.message_properties(),
        }
        return f"data: {json.dumps(message)}\ndata: [DONE]\n"
