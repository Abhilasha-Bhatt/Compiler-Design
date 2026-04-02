from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import json
from bs4 import BeautifulSoup   # ✅ NEW

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


# FORMAT HTML FUNCTION (NEW)
def format_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.prettify()


# UI ROUTE
@app.route("/")
def home():
    return render_template("index.html")


# PREVIEW ROUTE (NEW)
@app.route("/preview")
def preview():
    try:
        with open("outputs/output.html", "r") as f:
            return f.read()
    except:
        return "<h2>No Preview Available</h2>"


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


# MAIN PROCESS
@app.route("/process", methods=["POST"])
def process():

    file = request.files.get("file")
    content = ""

    if file:
        content = file.read().decode("utf-8")

    # -------- LEXER --------
    tokens = tokenize(content)
    save_tokens(tokens)

    # -------- PARSER --------
    parser = Parser(tokens)
    ast = parser.parse_document()
    save_ast(ast)

    # -------- VALIDATION --------
    validate(ast)

    # -------- OPTIMIZATION --------
    ast = optimize(ast)

    # -------- JSON --------
    json_output = ast_to_json(ast)

    with open(f"{OUTPUT_DIR}/ast.json", "w") as f:
        json.dump(json_output, f, indent=2)

    # -------- HTML OUTPUT (FORMATTED) --------
    raw_html = generate_html(ast)
    html_output = format_html(raw_html)

    with open(f"{OUTPUT_DIR}/output.html", "w") as f:
        f.write(html_output)

    # -------- TYPST --------
    typst_output = generate_typst(ast)

    with open(f"{OUTPUT_DIR}/output.typ", "w") as f:
        f.write(typst_output)

    # -------- READ FILES --------
    with open(f"{OUTPUT_DIR}/tokens.txt") as f:
        tokens_data = f.read()

    with open(f"{OUTPUT_DIR}/ast.txt") as f:
        ast_data = f.read()

    with open(f"{OUTPUT_DIR}/ast.json") as f:
        json_data = f.read()

    return jsonify({
        "html": html_output,
        "typst": typst_output,
        "tokens": tokens_data,
        "ast": ast_data,
        "json": json_data
    })


if __name__ == "__main__":
    app.run(debug=True)