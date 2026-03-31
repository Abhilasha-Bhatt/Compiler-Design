from parser.ast_nodes import *

class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        self.pos += 1

    # ---------------- MAIN ----------------
    def parse_document(self):
        nodes = []

        while self.current() is not None:
            node = self.parse_block()
            if node:
                nodes.append(node)

        return Document(nodes)

    # ---------------- BLOCK ----------------
    def parse_block(self):
        token = self.current()

        if token.type == "HEADING":
            return self.parse_heading()

        elif token.type in ["LIST_ITEM", "ORDERED_LIST_ITEM"]:
            return self.parse_list()

        elif token.type == "CODE_BLOCK_START":
            return self.parse_code_block()

        elif token.type == "BLOCKQUOTE":
            return self.parse_blockquote()

        elif token.type == "TABLE_ROW":
            return self.parse_table()

        else:
            return self.parse_paragraph()

    # ---------------- HEADING ----------------
    def parse_heading(self):
        level = self.current().value
        self.advance()

        text_token = self.current()
        self.advance()

        return Heading(level, Text(text_token.value))

    # ---------------- PARAGRAPH ----------------
    def parse_paragraph(self):
        children = []

        while self.current() is not None and self.current().type != "NEWLINE":

            token = self.current()

            if token.type == "TEXT":
                children.append(Text(token.value))
                self.advance()

            elif token.type == "BOLD":
                children.append(self.parse_bold())

            elif token.type == "ITALIC":
                children.append(self.parse_italic())

            elif token.type == "INLINE_CODE":
                children.append(InlineCode(token.value))
                self.advance()

            elif token.type == "LINK":
                text, url = token.value
                children.append(Link(text, url))
                self.advance()

            elif token.type == "IMAGE":
                alt, url = token.value
                children.append(Image(alt, url))
                self.advance()

            else:
                self.advance()

        if self.current() and self.current().type == "NEWLINE":
            self.advance()

        return Paragraph(children)

    # ---------------- BOLD ----------------
    def parse_bold(self):
        self.advance()
        text_token = self.current()
        self.advance()

        if self.current() and self.current().type == "BOLD":
            self.advance()
        else:
            raise Exception("Unclosed bold formatting")

        return Bold(Text(text_token.value))

    # ---------------- ITALIC ----------------
    def parse_italic(self):
        self.advance()
        text_token = self.current()
        self.advance()

        if self.current() and self.current().type == "ITALIC":
            self.advance()
        else:
            raise Exception("Unclosed italic formatting")

        return Italic(Text(text_token.value))

    # ---------------- LIST ----------------
    def parse_list(self):
        items = []
        ordered = self.current().type == "ORDERED_LIST_ITEM"

        while self.current() and self.current().type in ["LIST_ITEM", "ORDERED_LIST_ITEM"]:
            self.advance()
            text_token = self.current()
            self.advance()
            items.append(ListItem(Text(text_token.value)))

        return ListNode(items, ordered)

    # ---------------- CODE BLOCK ----------------
    def parse_code_block(self):
        lang = self.current().value
        self.advance()

        content = []

        while self.current() and self.current().type != "CODE_BLOCK_END":
            content.append(self.current().value)
            self.advance()

        self.advance()

        return CodeBlock(lang, "\n".join(content))

    # ---------------- BLOCKQUOTE ----------------
    def parse_blockquote(self):
        content = self.current().value
        self.advance()
        return BlockQuote(Text(content))

    # ---------------- TABLE ----------------
    def parse_table(self):
        rows = []

        while self.current() and self.current().type == "TABLE_ROW":
            rows.append(self.current().value)
            self.advance()

        return Table(rows)


# ---------------- JSON CONVERTER (BONUS) ----------------
def ast_to_json(node):

    if node is None:
        return None

    result = {
        "type": node.__class__.__name__
    }

    if hasattr(node, "level"):
        result["level"] = node.level

    if hasattr(node, "value"):
        result["value"] = node.value

    if hasattr(node, "url"):
        result["url"] = node.url

    if hasattr(node, "alt"):
        result["alt"] = node.alt

    if hasattr(node, "child"):
        result["child"] = ast_to_json(node.child)

    if hasattr(node, "children"):
        result["children"] = [ast_to_json(c) for c in node.children]

    if hasattr(node, "items"):
        result["items"] = [ast_to_json(i) for i in node.items]

    if hasattr(node, "content"):
        if isinstance(node.content, list):
            result["content"] = [ast_to_json(c) for c in node.content]
        elif hasattr(node.content, "value"):
            result["content"] = node.content.value

    return result