from _typeshed import Incomplete

SPIECE_UNDERLINE: str

class HuggingfaceTokenizerHelper:
    tokenizer: Incomplete
    token_has_space_prefix: Incomplete
    def __init__(self, tokenizer) -> None: ...
    def encode_prompt(self, prompt: str | list[dict[str, str]]) -> list[int]: ...
    def no_strip_decode(self, tokens): ...
    def extract_vocabulary(self) -> tuple[list[tuple[int, str]], int]: ...
