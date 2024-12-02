from ChatCompletionResponder import ChatCompletionResponder


import json


class ToolCallResponder(ChatCompletionResponder):
    def __init__(
        self, model_name: str, functions: list[dict], is_legacy_function_call: bool
    ):
        super().__init__(model_name)

        self.is_legacy_function_call = is_legacy_function_call

        function_schemas = [
            {
                "type": "object",
                "properties": {
                    "name": {"type": "const", "const": fn.name},
                    "arguments": fn.parameters,
                },
                "required": ["name", "arguments"],
            }
            for fn in functions
        ]
        if len(function_schemas) == 1:
            self.schema = function_schemas[0]
            self.tool_prompt = self._one_tool_prompt(functions[0], function_schemas[0])
        elif is_legacy_function_call:  # Only allows one function to be called.
            self.schema = {"oneOf": function_schemas}
            self.tool_prompt = self._select_tool_prompt(functions, function_schemas)
        else:
            self.schema = {"type": "array", "items": {"anyOf": function_schemas}}
            self.tool_prompt = self._multiple_tool_prompt(functions, function_schemas)

    def translate_reason(self, reason):
        if reason == "end":
            if self.is_legacy_function_call:
                return "function_call"
            return "tool_calls"
        return super().translate_reason(reason)

    def generation_stopped(
        self,
        stop_reason: str,
        prompt_tokens: int,
        completion_tokens: int,
    ):
        finish_reason = self.translate_reason(stop_reason)
        if finish_reason == "tool_calls":
            tool_calls = json.loads(self.content)
            if not isinstance(tool_calls, list):
                # len(functions) == 1 was special cased
                tool_calls = [tool_calls]
            message = {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": f"call_{self.id}_{i}",
                        "type": "function",
                        "function": {
                            "name": function_call["name"],
                            "arguments": json.dumps(function_call["arguments"]),
                        },
                    }
                    for i, function_call in enumerate(tool_calls)
                ],
            }
        elif finish_reason == "function_call":
            function_call = json.loads(self.content)
            message = {
                "role": "assistant",
                "function_call": {
                    "name": function_call["name"],
                    "arguments": json.dumps(function_call["arguments"]),
                },
            }
        else:
            message = None
        return {
            "choices": [
                {"index": 0, "message": message, "finish_reason": finish_reason}
            ],
            **self.format_usage(prompt_tokens, completion_tokens),
            **self.message_properties(),
        }

    def _one_tool_prompt(self, tool, tool_schema):
        return f"""
You are a helpful assistant with access to a tool that you must invoke to answer the user's request.
The tool is:
Tool {tool.name}: {tool.description}
Invocation schema: {json.dumps(tool_schema)}
Your answer is a JSON object according to the invocation schema in order to answer the user request below.
"""

    def _multiple_tool_prompt(self, tools, tool_schemas, separator="\n"):
        return f"""
You are a helpful assistant with access to tools that you must invoke to answer the user's request.
The following tools are available:
{separator.join([ f'''
Tool {tool.name}: {tool.description}
Invocation schema: {json.dumps(tool_schema)}
''' for tool, tool_schema in zip(tools, tool_schemas) ])}
Your answer is a JSON array with one or more tool invocations according to the appropriate schema(s)
in order to answer the user request below.
"""

    def _select_tool_prompt(self, tools, tool_schemas, separator="\n"):
        return f"""
You are a helpful assistant with access to tools that you must invoke to answer the user's request.
The following tools are available:
{separator.join([ f'''
Function {tool.name}: {tool.description}
Tool schema: {json.dumps(tool_schema)}
''' for tool, tool_schema in zip(tools, tool_schemas) ])}
Your answer is a JSON object according to the invocation schema of the most appropriate tool to use
to answer the user request below.
"""
