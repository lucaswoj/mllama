from dotenv import load_dotenv
import os
from enum import Enum
from traceback import format_exc
from typing import Literal, List, Optional, Union
from fastapi import FastAPI, Request, status
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from llm_structured_output.util.output import info, warning, debug
from typing import Optional, Union
from llm_structured_output.util.output import info, bold, bolddim, debug
from chat.Model import Model
from chat.V1Function import V1Function
from chat.ChatCompletionResponder import ChatCompletionResponder
from chat.ChatCompletionStreamingResponder import ChatCompletionStreamingResponder
from chat.ToolCallResponder import ToolCallResponder
from chat.ToolCallStreamingResponder import ToolCallStreamingResponder
from llm_structured_output.util.output import debug, info
import json

load_dotenv()


model = Model()
info("Loading model...")
try:
    model_path = os.environ["MODEL_PATH"]
    model.load(model_path)
except KeyError:
    warning("Need to specify MODEL_PATH environment variable")


app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}"
    warning(f"RequestValidationError: {exc_str}")
    content = {"error": exc_str}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@app.get("/status")
def get_status():
    return {"status": "OK"}


class V1ChatMessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class V1ChatMessage(BaseModel):
    role: V1ChatMessageRole
    content: str


class V1ToolFunction(BaseModel):
    type: Literal["function"]
    function: V1Function


class V1ToolChoiceKeyword(str, Enum):
    AUTO = "auto"
    NONE = "none"


class V1ToolChoiceFunction(BaseModel):
    type: Optional[Literal["function"]] = None
    name: str


class V1ToolOptions(BaseModel):  # Non-standard, our addition.
    # We automatically add instructions with the JSON schema
    # for the tool calls to the prompt. This option disables
    # it and is useful when the user prompt already includes
    # the schema and relevant instructions.
    no_prompt_steering: bool = False


class V1ResponseFormatType(str, Enum):
    JSON_OBJECT = "json_object"


class V1ResponseFormat(BaseModel):
    type: V1ResponseFormatType
    # schema is our addition, not an OpenAI API parameter
    schema: Optional[str] = None  # type: ignore


class V1StreamOptions(BaseModel):
    include_usage: bool = False


class V1ChatCompletionsRequest(BaseModel):
    model: str = "default"
    max_tokens: int = 1000
    temperature: float = 0.0
    messages: List[V1ChatMessage]
    # The 'functions' and 'function_call' fields have been dreprecated and
    # replaced with 'tools' and 'tool_choice', that work similarly but allow
    # for multiple functions to be invoked.
    functions: Optional[List[V1Function]] = None
    function_call: Optional[Union[V1ToolChoiceKeyword, V1ToolChoiceFunction]] = None
    tools: Optional[List[V1ToolFunction]] = None
    tool_choice: Optional[Union[V1ToolChoiceKeyword, V1ToolChoiceFunction]] = None
    tool_options: Optional[V1ToolOptions] = None
    response_format: Optional[V1ResponseFormat] = None
    stream: bool = False
    stream_options: Optional[V1StreamOptions] = None


@app.post("/v1/chat/completions")
async def post_v1_chat_completions(request: V1ChatCompletionsRequest):
    debug("REQUEST", request)
    if request.stream:

        async def get_content():
            try:
                async for message in chat(request):
                    yield message

            except Exception as e:
                warning(format_exc())
                yield 'data: {"choices": [{"index": 0, "finish_reason": "error: ' + str(
                    e
                ) + '"}]}'

        return StreamingResponse(
            content=get_content(),
            media_type="text/event-stream",
        )
    else:
        try:
            response = await anext(chat(request))

        except Exception as e:
            warning(format_exc())
            content = {"error": str(e)}
            response = JSONResponse(
                content=content, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        debug("RESPONSE", response)
        return response


async def chat(request: V1ChatCompletionsRequest):
    messages = request.messages[:]

    # Extract valid functions from the request.
    functions = []
    is_legacy_function_call = False
    if request.tool_choice == "none" or request.tools is None:
        pass
    elif request.tool_choice == "auto":
        functions = [tool.function for tool in request.tools if tool.type == "function"]
    elif request.tool_choice is not None:
        functions = [
            next(
                tool.function
                for tool in request.tools
                if tool.type == "function"
                and tool.function.name == request.tool_choice.name
            )
        ]
    elif request.function_call == "none" or request.functions is None:
        pass
    elif request.function_call == "auto":
        functions = request.functions
        is_legacy_function_call = True
    elif request.function_call is not None:
        functions = [
            next(
                fn for fn in request.functions if fn.name == request.function_call.name
            )
        ]
        is_legacy_function_call = True

    model_name = model_path
    schema = None
    responder: ChatCompletionResponder
    if functions:
        # If the request includes functions, create a system prompt to instruct the LLM
        # to use tools, and assemble a JSON schema to steer the LLM output.
        if request.stream:
            responder = ToolCallStreamingResponder(
                model_name,
                functions,
                is_legacy_function_call,
                model,
            )
        else:
            responder = ToolCallResponder(
                model_name, functions, is_legacy_function_call
            )
        if not (request.tool_options and request.tool_options.no_prompt_steering):
            messages.insert(
                0,
                V1ChatMessage(
                    role=V1ChatMessageRole.SYSTEM,
                    content=responder.tool_prompt,
                ),
            )
        schema = responder.schema
    else:
        if request.response_format:
            assert request.response_format.type == V1ResponseFormatType.JSON_OBJECT
            # The request may specify a JSON schema (this option is not in the OpenAI API)
            if request.response_format.schema:
                schema = json.loads(request.response_format.schema)
            else:
                schema = {"type": "object"}
        if request.stream:
            responder = ChatCompletionStreamingResponder(model_name, schema, model)
        else:
            responder = ChatCompletionResponder(model_name)

    if schema is not None:
        debug("Using schema:", schema)

    info("Starting generation...")

    prompt_tokens = None

    for result in model.completion(
        (msg.model_dump() for msg in messages),
        schema=schema,
        max_tokens=request.max_tokens,
        temp=request.temperature,
        cache_prompt=True,
    ):
        if result["op"] == "evaluatedPrompt":
            prompt_tokens = result["token_count"]
        elif result["op"] == "generatedTokens":
            message = responder.generated_tokens(result["text"])
            if message:
                yield message
        elif result["op"] == "stop":
            completion_tokens = result["token_count"]
            yield responder.generation_stopped(
                result["reason"], prompt_tokens or 0, completion_tokens
            )
        else:
            assert False
