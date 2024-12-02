class RejectedCompletion(Exception):
    """
    It's rare, but sometimes we reach a state where it's not possible to
    advance the acceptor. For example, when closing a JSON string we get
    a higher probability for slanted quotes than straight ones and select
    the wrong token. At that point, the LLM will continue generating with
    the prior that the string is closed, but our acceptor will remain in
    the string-accepting state. This can indicate an issue with the
    tokenizer vocabulary passed to the acceptor, or a bug in the code
    used to decode tokens from the LLM. If none of these apply, check that
    the LLM is actually able to generate JSON, although most are.
    """
