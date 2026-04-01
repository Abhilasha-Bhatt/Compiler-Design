class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __repr__(self):
        if self.value is not None:
            return f"{self.type}({self.value})"
        return f"{self.type}"


# Token Types Reference
TOKEN_TYPES = [
    "HEADING",
    "TEXT",
    "BOLD",
    "ITALIC",
    "LIST_ITEM",
    "ORDERED_LIST_ITEM",
    "CODE_BLOCK_START",
    "CODE_BLOCK_END",
    "INLINE_CODE",
    "LINK",
    "IMAGE",
    "BLOCKQUOTE",
    "TABLE_ROW",
    "NEWLINE",
]