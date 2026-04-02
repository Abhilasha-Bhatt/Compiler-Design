from parser.ast_nodes import *

def optimize(node):

    def visit(n):

        # -------- MERGE TEXT NODES --------
        if isinstance(n, Paragraph):
            new_children = []
            buffer = ""

            for child in n.children:
                if isinstance(child, Text):
                    buffer += child.value
                else:
                    if buffer:
                        new_children.append(Text(buffer))
                        buffer = ""
                    new_children.append(child)

            if buffer:
                new_children.append(Text(buffer))

            n.children = new_children

        # -------- REMOVE EMPTY PARAGRAPHS --------
        if isinstance(n, Paragraph) and len(n.children) == 0:
            return None

        # -------- RECURSION --------
        if hasattr(n, "children"):
            n.children = [visit(c) for c in n.children if visit(c) is not None]

        if hasattr(n, "child"):
            n.child = visit(n.child)

        if hasattr(n, "items"):
            n.items = [visit(i) for i in n.items if visit(i) is not None]

        return n

    return visit(node)