from parser.ast_nodes import *

def validate(node):
    errors = []

    def visit(n):

        # -------- CHECK EMPTY TEXT --------
        if isinstance(n, Text):
            if not n.value or n.value.strip() == "":
                errors.append("Empty text node found")

        # -------- CHECK LINK --------
        if isinstance(n, Link):
            if not n.url.startswith("http"):
                errors.append(f"Invalid URL: {n.url}")

        # -------- CHECK IMAGE --------
        if isinstance(n, Image):
            if not n.url:
                errors.append("Image missing URL")

        # -------- CHECK HEADING --------
        if isinstance(n, Heading):
            if n.level < 1 or n.level > 6:
                errors.append(f"Invalid heading level: {n.level}")

        # -------- RECURSION --------
        if hasattr(n, "children"):
            for c in n.children:
                visit(c)

        if hasattr(n, "child"):
            visit(n.child)

        if hasattr(n, "items"):
            for i in n.items:
                visit(i)

    visit(node)

    if errors:
        print("\n⚠️ VALIDATION ERRORS:")
        for e in errors:
            print("-", e)
    else:
        print("\n✅ No semantic errors found!")

    return errors