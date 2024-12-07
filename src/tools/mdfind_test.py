from tools.mdfind import mdfind


def smoke_test():
    mdfind("Hello", limit=1)
