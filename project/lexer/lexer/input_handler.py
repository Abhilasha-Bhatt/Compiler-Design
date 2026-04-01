import os

def read_file():
    path = input("Enter path of Markdown (.md) file: ").strip()

    if not os.path.exists(path):
        print("❌ Error: File not found!")
        return None

    if not path.endswith(".md"):
        print("❌ Error: Please provide a .md file!")
        return None

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if len(content.strip()) == 0:
        print("❌ Error: File is empty!")
        return None

    print(f"\n✅ Processing file: {path}\n")
    return content