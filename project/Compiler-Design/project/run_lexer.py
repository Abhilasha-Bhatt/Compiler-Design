import json
from lexer.input_handler import read_file
from lexer.tokenizer import tokenize
from parser import Parser, ast_to_json


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


def main():
    text = read_file()

    if text:
        tokens = tokenize(text)

        parser = Parser(tokens)
        ast = parser.parse_document()

        print("\n🌳 AST STRUCTURE:\n")
        print_ast(ast)

        # -------- JSON OUTPUT --------
        json_output = ast_to_json(ast)

        print("\n📦 AST IN JSON:\n")
        print(json.dumps(json_output, indent=2))

        # Save JSON
        with open("ast_output.json", "w") as f:
            json.dump(json_output, f, indent=2)

        print("\n✅ JSON saved to ast_output.json")


if __name__ == "__main__":
    main()