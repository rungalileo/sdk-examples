import json, os, re, sys


def get_notebook_pip_commands(nb_path):
    # Clean up the path - remove quotes if present
    if nb_path:
        nb_path = nb_path.strip().strip("\"'")

    if not nb_path or not os.path.exists(nb_path):
        print(f"Error: Notebook path '{nb_path}' not found or invalid", file=sys.stderr)
        sys.exit(1)

    try:
        with open(nb_path, "r", encoding="utf-8") as f:
            nb = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON in {nb_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to read notebook {nb_path}: {e}", file=sys.stderr)
        sys.exit(1)

    install_cmds = []

    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = cell.get("source", [])
        if isinstance(src, str):
            cell_content = src
        else:
            cell_content = "".join(src)

        # Look for pip install commands that may span multiple lines
        # First, handle line continuations in the entire cell content
        cell_content_clean = re.sub(r"\\\s*\n\s*", " ", cell_content)

        # Pattern to match !pip or pip install commands
        pip_pattern = re.compile(
            r"^[!%]?\s*pip\s+(?:-q\s+)?install\s+(.+?)$", re.MULTILINE | re.IGNORECASE
        )

        matches = pip_pattern.findall(cell_content_clean)
        for match in matches:
            # Clean up the match - remove extra whitespace, quotes
            packages = match.strip()
            # Remove extra whitespace
            packages = re.sub(r"\s+", " ", packages).strip()
            # Remove quotes around package names but preserve --flags
            packages = re.sub(r'(?<!\-)[\'"]([^-\s][^\'"]*)[\'"]', r"\1", packages)
            # Remove trailing % or other unwanted characters
            packages = re.sub(r"[%\s]+$", "", packages)
            # Skip if it's a comment line or empty
            if packages and not packages.startswith("#"):
                install_cmds.append(f"python -m pip install {packages}")

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for c in install_cmds:
        if c not in seen:
            seen.add(c)
            unique.append(c)

    if unique:
        with open("nb_pip_commands.txt", "w", encoding="utf-8") as out:
            out.write("\n".join(unique))
        print(f"Wrote {len(unique)} pip install command(s) to nb_pip_commands.txt")
    else:
        # Create empty file if no commands found
        with open("nb_pip_commands.txt", "w", encoding="utf-8") as out:
            out.write("")
        print("No pip install commands found in notebook cells")


if __name__ == "__main__":
    nb_file = os.environ.get("NB_FILE")
    if not nb_file:
        print("Error: NB_FILE environment variable not set", file=sys.stderr)
        sys.exit(1)
    get_notebook_pip_commands(nb_file)
