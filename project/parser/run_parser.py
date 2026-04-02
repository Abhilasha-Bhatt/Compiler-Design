from lexer.input_handler import read_file
from lexer.tokenizer import tokenize
from parser import Parser


def print_ast(node, indent=0):
    print(" " * indent + node.__class__.__name__)

    if hasattr(node, "children"):
        for child in node.children:
            print_ast(child, indent + 2)

    if hasattr(node, "child"):
        print_ast(node.child, indent + 2)

    if hasattr(node, "items"):
        for item in node.items:
            print_ast(item, indent + 2)

    if hasattr(node, "content") and isinstance(node.content, list):
        for c in node.content:
            print_ast(c, indent + 2)


def main():
    text = read_file()

    if text:
        tokens = tokenize(text)

        parser = Parser(tokens)
        ast = parser.parse_document()

        print("\n AST STRUCTURE:\n")
        print_ast(ast)


if __name__ == "__main__":
    main()