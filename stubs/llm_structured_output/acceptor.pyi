from .util.tokentrie import TokenTrie as TokenTrie
from _typeshed import Incomplete
from typing import Iterable, Tuple

class TokenAcceptor:
    @classmethod
    def prepare_vocabulary(cls, vocabulary: Iterable[tuple[int, str]]) -> TokenTrie: ...
    @classmethod
    def match_all(
        cls, cursors: Iterable[TokenAcceptor.Cursor], trie: TokenTrie
    ) -> int: ...
    @classmethod
    def debug_match_all(
        cls,
        cursors: Iterable[TokenAcceptor.Cursor],
        trie: TokenTrie,
        debug_output_fn=...,
    ) -> int: ...
    @classmethod
    def advance_all(
        cls, cursors: Iterable[TokenAcceptor.Cursor], char: str
    ) -> list[TokenAcceptor.Cursor]: ...
    def get_cursors(self) -> Iterable[TokenAcceptor.Cursor]: ...

    class Cursor:
        def __init__(self, acceptor: TokenAcceptor) -> None: ...
        def clone(self): ...
        def matches_all(self) -> bool: ...
        def select(self, candidate_chars: set[str]) -> Iterable[str]: ...
        def advance(self, char: str) -> Iterable[TokenAcceptor.Cursor]: ...
        def in_accepted_state(self) -> bool: ...
        def get_value(self) -> str: ...
        def get_value_path(self): ...
        def is_in_value(self): ...
        def prune(self, trie: TokenTrie) -> Iterable[Tuple[str, TokenTrie]]: ...
        def match(self, trie: TokenTrie) -> int: ...
        def debug_match(
            self, trie: TokenTrie, debug_output_fn=..., debug_indent: int = 1
        ) -> int: ...

class AcceptedState(TokenAcceptor.Cursor):
    cursor: Incomplete
    def __init__(self, cursor: TokenAcceptor.Cursor) -> None: ...
    def in_accepted_state(self): ...
    def get_value(self): ...

class CharAcceptor(TokenAcceptor):
    charset: Incomplete
    def __init__(self, charset: Iterable[str]) -> None: ...

    class Cursor(TokenAcceptor.Cursor):
        acceptor: Incomplete
        value: Incomplete
        def __init__(self, acceptor, value: Incomplete | None = None) -> None: ...
        def select(self, candidate_chars): ...
        def advance(self, char): ...
        def get_value(self): ...

class TextAcceptor(TokenAcceptor):
    text: Incomplete
    def __init__(self, text: str) -> None: ...

    class Cursor(TokenAcceptor.Cursor):
        acceptor: Incomplete
        pos: Incomplete
        def __init__(self, acceptor, pos: int = 0) -> None: ...
        def select(self, candidate_chars): ...
        def advance(self, char): ...
        def get_value(self) -> str: ...

class StateMachineAcceptor(TokenAcceptor):
    graph: Incomplete
    initial_state: Incomplete
    end_states: Incomplete
    def __init__(
        self,
        graph: Incomplete | None = None,
        initial_state: Incomplete | None = None,
        end_states: Incomplete | None = None,
    ) -> None: ...
    def get_edges(self, state): ...
    def get_cursors(self): ...
    def advance_cursor(self, cursor, char): ...

    class Cursor(TokenAcceptor.Cursor):
        acceptor: Incomplete
        accept_history: Incomplete
        current_state: Incomplete
        transition_cursor: Incomplete
        target_state: Incomplete
        consumed_character_count: int
        def __init__(self, acceptor) -> None: ...
        def matches_all(self): ...
        def select(self, candidate_chars): ...
        def prune(self, trie): ...
        def advance(self, char): ...
        def start_transition(self, transition_acceptor, target_state) -> bool: ...
        def complete_transition(
            self, transition_value, target_state, is_end_state
        ) -> bool: ...
        def get_value(self): ...
        def is_in_value(self): ...
        def get_value_path(self): ...

    class EmptyTransitionAcceptor(TokenAcceptor):
        def get_cursors(self): ...

        class Cursor(TokenAcceptor.Cursor):
            def get_value(self): ...

    EmptyTransition: Incomplete

class SequenceAcceptor(StateMachineAcceptor):
    def __init__(self, acceptors) -> None: ...

    class Cursor(StateMachineAcceptor.Cursor): ...

class WaitForAcceptor(TokenAcceptor):
    wait_for_acceptor: Incomplete
    def __init__(self, wait_for_acceptor: TokenAcceptor) -> None: ...

    class Cursor(TokenAcceptor.Cursor):
        acceptor: Incomplete
        cursors: Incomplete
        def __init__(self, acceptor, cursors: Incomplete | None = None) -> None: ...
        def matches_all(self): ...
        def advance(self, char): ...
        def get_value(self): ...
