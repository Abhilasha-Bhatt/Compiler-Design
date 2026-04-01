from parser.ast_nodes import *

def generate_typst(node):

    if isinstance(node, Document):
        return "\n".join(generate_typst(c) for c in node.children)

    if isinstance(node, Heading):
        return "=" * node.level + " " + generate_typst(node.content)

    if isinstance(node, Paragraph):
        return "".join(generate_typst(c) for c in node.children)

    if isinstance(node, Text):
        return node.value

    if isinstance(node, Bold):
        return f"*{generate_typst(node.child)}*"

    if isinstance(node, Italic):
        return f"_{generate_typst(node.child)}_"

    if isinstance(node, ListNode):
        prefix = "+" if node.ordered else "-"
        return "\n".join(f"{prefix} {generate_typst(i.content)}" for i in node.items)

    if isinstance(node, CodeBlock):
        return f"```{node.language}\n{node.content}\n```"

    if isinstance(node, InlineCode):
        return f"`{node.value}`"

    if isinstance(node, Link):
        return f"{node.text} ({node.url})"

    if isinstance(node, Image):
        return f"[Image: {node.alt}]"

    if isinstance(node, BlockQuote):
        return f"> {generate_typst(node.content)}"

    if isinstance(node, Table):
        return "\n".join(node.rows)

    return ""