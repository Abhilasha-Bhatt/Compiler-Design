from lexer.tokens import Token
import re

def tokenize(text):
    tokens = []
    lines = text.split("\n")

    in_code_block = False

    for line in lines:

        # ---------- CODE BLOCK ----------
        if line.startswith("```"):
            if not in_code_block:
                lang = line.replace("```", "").strip()
                tokens.append(Token("CODE_BLOCK_START", lang))
                in_code_block = True
            else:
                tokens.append(Token("CODE_BLOCK_END"))
                in_code_block = False
            continue

        if in_code_block:
            tokens.append(Token("TEXT", line))
            continue

        # ---------- EMPTY LINE ----------
        if line.strip() == "":
            tokens.append(Token("NEWLINE"))
            continue

        # ---------- HEADING ----------
        if line.startswith("#"):
            level = 0
            while level < len(line) and line[level] == "#":
                level += 1

            content = line[level:].strip()
            tokens.append(Token("HEADING", level))
            tokens.append(Token("TEXT", content))
            continue

        # ---------- BLOCKQUOTE ----------
        if line.startswith(">"):
            tokens.append(Token("BLOCKQUOTE", line[1:].strip()))
            continue

        # ---------- UNORDERED LIST ----------
        if line.startswith("- "):
            tokens.append(Token("LIST_ITEM"))
            tokens.append(Token("TEXT", line[2:].strip()))
            continue

        # ---------- ORDERED LIST ----------
        if re.match(r'\d+\.\s', line):
            tokens.append(Token("ORDERED_LIST_ITEM"))
            content = re.sub(r'\d+\.\s', '', line)
            tokens.append(Token("TEXT", content))
            continue

        # ---------- TABLE ----------
        if "|" in line:
            tokens.append(Token("TABLE_ROW", line.strip()))
            continue

        # ---------- INLINE ----------
        tokens.extend(tokenize_inline(line))

    return tokens


# -------- INLINE TOKENIZER --------
def tokenize_inline(line):
    tokens = []

    # IMAGE ![alt](url)
    for match in re.finditer(r'!\[(.*?)\]\((.*?)\)', line):
        tokens.append(Token("IMAGE", (match.group(1), match.group(2))))
        line = line.replace(match.group(0), "")

    # LINK [text](url)
    for match in re.finditer(r'\[(.*?)\]\((.*?)\)', line):
        tokens.append(Token("LINK", (match.group(1), match.group(2))))
        line = line.replace(match.group(0), "")

    # INLINE CODE `code`
    parts = re.split(r'(`.*?`)', line)

    for part in parts:
        if part.startswith("`") and part.endswith("`"):
            tokens.append(Token("INLINE_CODE", part[1:-1]))
        else:
            # BOLD **text**
            subparts = re.split(r'(\*\*.*?\*\*)', part)

            for sp in subparts:
                if sp.startswith("**") and sp.endswith("**"):
                    tokens.append(Token("BOLD"))
                    tokens.append(Token("TEXT", sp[2:-2]))
                    tokens.append(Token("BOLD"))
                else:
                    # ITALIC *text*
                    italics = re.split(r'(\*.*?\*)', sp)

                    for it in italics:
                        if it.startswith("*") and it.endswith("*"):
                            tokens.append(Token("ITALIC"))
                            tokens.append(Token("TEXT", it[1:-1]))
                            tokens.append(Token("ITALIC"))
                        elif it.strip() != "":
                            tokens.append(Token("TEXT", it))

    return tokens