class Node:
    pass


class Document(Node):
    def __init__(self, children):
        self.children = children


class Heading(Node):
    def __init__(self, level, content):
        self.level = level
        self.content = content


class Paragraph(Node):
    def __init__(self, children):
        self.children = children


class Text(Node):
    def __init__(self, value):
        self.value = value


class Bold(Node):
    def __init__(self, child):
        self.child = child


class Italic(Node):
    def __init__(self, child):
        self.child = child


class ListNode(Node):
    def __init__(self, items, ordered=False):
        self.items = items
        self.ordered = ordered


class ListItem(Node):
    def __init__(self, content):
        self.content = content


class CodeBlock(Node):
    def __init__(self, language, content):
        self.language = language
        self.content = content


class InlineCode(Node):
    def __init__(self, value):
        self.value = value


class Link(Node):
    def __init__(self, text, url):
        self.text = text
        self.url = url


class Image(Node):
    def __init__(self, alt, url):
        self.alt = alt
        self.url = url


class BlockQuote(Node):
    def __init__(self, content):
        self.content = content


class Table(Node):
    def __init__(self, rows):
        self.rows = rows