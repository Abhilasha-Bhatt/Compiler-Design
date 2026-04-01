from parser.ast_nodes import *

def generate_html(node):

    if isinstance(node, Document):
        return "".join(generate_html(c) for c in node.children)

    if isinstance(node, Heading):
        return f"<h{node.level}>{generate_html(node.content)}</h{node.level}>"

    if isinstance(node, Paragraph):
        return "<p>" + "".join(generate_html(c) for c in node.children) + "</p>"

    if isinstance(node, Text):
        return node.value

    if isinstance(node, Bold):
        return f"<b>{generate_html(node.child)}</b>"

    if isinstance(node, Italic):
        return f"<i>{generate_html(node.child)}</i>"

    if isinstance(node, ListNode):
        tag = "ol" if node.ordered else "ul"
        items = "".join(f"<li>{generate_html(i.content)}</li>" for i in node.items)
        return f"<{tag}>{items}</{tag}>"

    if isinstance(node, CodeBlock):
        return f"<pre><code>{node.content}</code></pre>"

    if isinstance(node, InlineCode):
        return f"<code>{node.value}</code>"

    if isinstance(node, Link):
        return f'<a href="{node.url}">{node.text}</a>'

    if isinstance(node, Image):
        return f'<img src="{node.url}" alt="{node.alt}"/>'

    if isinstance(node, BlockQuote):
        return f"<blockquote>{generate_html(node.content)}</blockquote>"

    if isinstance(node, Table):
        rows = ""
        for row in node.rows:
            cells = row.strip("|").split("|")
            row_html = "".join(f"<td>{c.strip()}</td>" for c in cells)
            rows += f"<tr>{row_html}</tr>"
        return f"<table>{rows}</table>"

    return ""