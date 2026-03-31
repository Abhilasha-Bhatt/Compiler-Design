from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import json

from lexer.tokenizer import tokenize
from parser.parser import Parser, ast_to_json
from semantic.validator import validate
from semantic.optimizer import optimize
from generator.html_generator import generate_html
from generator.typst_generator import generate_typst

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ✅ MAIN UI ROUTE (IMPORTANT)
@app.route("/")
def home():
    return render_template("index.html")


# -------- SAVE FUNCTIONS --------
def save_tokens(tokens):
    with open(f"{OUTPUT_DIR}/tokens.txt", "w") as f:
        for t in tokens:
            f.write(str(t) + "\n")


def save_ast(ast):
    def print_ast(node, indent=0):
        result = " " * indent + node.__class__.__name__ + "\n"

        if hasattr(node, "children"):
            for c in node.children:
                result += print_ast(c, indent + 2)

        if hasattr(node, "child"):
            result += print_ast(node.child, indent + 2)

        if hasattr(node, "items"):
            for i in node.items:
                result += print_ast(i, indent + 2)

        return result

    with open(f"{OUTPUT_DIR}/ast.txt", "w") as f:
        f.write(print_ast(ast))


# ✅ PROCESS ROUTE
@app.route("/process", methods=["POST"])
def process():

    file = request.files["file"]
    output_format = request.form.get("format")

    content = file.read().decode("utf-8")

    tokens = tokenize(content)
    save_tokens(tokens)

    parser = Parser(tokens)
    ast = parser.parse_document()
    save_ast(ast)

    validate(ast)
    ast = optimize(ast)

    json_output = ast_to_json(ast)

    with open(f"{OUTPUT_DIR}/ast.json", "w") as f:
        json.dump(json_output, f, indent=2)

    if output_format == "html":
        output = generate_html(ast)
        with open(f"{OUTPUT_DIR}/output.html", "w") as f:
            f.write(output)
    else:
        output = generate_typst(ast)
        with open(f"{OUTPUT_DIR}/output.typ", "w") as f:
            f.write(output)

    return jsonify({"result": output})


if __name__ == "__main__":
    app.run(debug=True)