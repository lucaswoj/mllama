from typing import Iterable

def count_set_bits(bitmap: int) -> int: ...
def highest_bit_set(bitmap: int) -> int: ...
def bitmap_complement(bitmap: int, set_size: int = None) -> int: ...
def enumerate_set_bits(bitmap: int) -> Iterable[int]: ...
def bias_logits(np, logits, accepted_token_bitmap): ...