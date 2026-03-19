#!/usr/bin/env python3
# -----------------------------------------------------------------------------
"""
Authors: Ran
Created: 2021-10-18 13:50:54
Revised: 2024-05-11 15:13:16
"""
# -----------------------------------------------------------------------------
# Rewrite of the "metadata" script from 2019
# -----------------------------------------------------------------------------

import sys
from datetime import datetime
from pathlib import Path

# -----------------------------------------------------------------------------
# UTILS
# -----------------------------------------------------------------------------


def save_file(fname: str, content: str | list[str], encoding: str = "utf-8") -> None:
    """Saves content to a file, creating the directory path if needed.

    Args:
        fname: Path to the file, with extension.
        content: String or list of strings to write, one per line.
        encoding: Encoding to use when writing the file.
    """
    Path(fname).parent.mkdir(parents=True, exist_ok=True)

    with open(fname, "w", encoding=encoding) as f:
        if isinstance(content, str):
            f.write(content)
        else:
            f.writelines(f"{line}\n" for line in content)


# -----------------------------------------------------------------------------


def load_file(
    fname: str,
    in_lines: bool = True,
    encoding: str = "utf-8",
) -> str | list[str]:
    """Loads a file as a list of lines or a single string.

    Args:
        fname: Path to the file, with extension.
        in_lines: If True, return a list of lines; if False, return the whole file as a string.
        encoding: Encoding to use when reading the file.

    Returns:
        List of lines if in_lines is True, otherwise the full file contents as a string.
    """
    if not Path(fname).is_file():
        raise FileNotFoundError(f"File {fname} does not exist")

    with open(fname, encoding=encoding) as f:
        return f.read().splitlines() if in_lines else f.read()


# -----------------------------------------------------------------------------


def print_help():
    print()
    print("Help   -----------------------------")
    print("?/-h\t-> Show this message")
    print("-v file\t-> View metadata")
    print("-m file\t-> Modify metadata")
    print("-c file\t-> Create metadata")
    print("-d file\t-> Delete metadata")
    print("------------------------------------")
    print()


# -----------------------------------------------------------------------------


def read_input():
    args = sys.argv[1:]
    help_flags = ["-h", "?", "-?", "--help"]
    option_flags = ["-v", "-m", "-c", "-d"]

    if not args or args[0] in help_flags:
        print_help()
        sys.exit()

    flag = args[0]

    if flag not in option_flags:
        print_help()
        sys.exit()

    if len(args) < 2:
        print()
        print("ERROR: Missing file argument")
        print_help()
        sys.exit()

    return flag, args[1]


# -----------------------------------------------------------------------------


def format_now(style):
    """Returns the current datetime formatted according to style settings."""
    fmt = f"%Y{style['date_sep']}%m{style['date_sep']}%d %H{style['time_sep']}%M{style['time_sep']}%S"
    if style["microsec"]:
        fmt += f"{style['microsec_sep']}%f"
    return datetime.now().strftime(fmt)


# -----------------------------------------------------------------------------


def show(file, file_type, ft, style):
    lines = load_file(file)

    if file_type == ".py":
        in_docstring = False
        for line in lines:
            if line.strip() == '"""' and not in_docstring:
                in_docstring = True
                continue
            if line.strip() == '"""' and in_docstring:
                break
            if in_docstring:
                print(line.rstrip())
    else:
        c = ft["comment"]
        for line in lines:
            if line.rstrip().startswith(c + style["indicator"]):
                print(line.rstrip())


# -----------------------------------------------------------------------------


def edit(file, file_type, ft, style):
    content = load_file(file)
    now = format_now(style)

    if file_type == ".py":
        for index, line in enumerate(content):
            if line.startswith(style["label_revised"] + ":"):
                content[index] = f"{style['label_revised']}: {now}"
    else:
        c = ft["comment"]
        e = ft.get("end", "")
        for index, line in enumerate(content):
            if line.startswith(c + style["indicator"] + f" {style['label_revised']}:"):
                content[index] = f"{c}{style['indicator']} {style['label_revised']}: \t{now}{e}"

    save_file(file, content)


# -----------------------------------------------------------------------------


def create(file, file_type, ft, style):
    content = load_file(file)
    now = format_now(style)

    if file_type == ".py":
        to_insert = [
            "#!/usr/bin/env python3",
            '"""',
            f"{style['label_author']}: {style['author']}",
            f"{style['label_created']}: {now}",
            f"{style['label_revised']}: {now}",
            '"""',
            "",
        ]
    else:
        c = ft["comment"]
        i = style["indicator"]
        e = ft.get("end", "")
        separator = f"{c} {'-' * (79 - len(c))}{e}"
        to_insert = [
            separator,
            f"{c}{i} {style['label_author']}: \t{style['author']}{e}",
            f"{c}{i} {style['label_created']}: \t{now}{e}",
            f"{c}{i} {style['label_revised']}: \t{now}{e}",
            separator,
            "",
        ]
        if ft.get("shebang"):
            to_insert.insert(0, ft["shebang"])

    # Strip existing header of the same length before prepending, so re-running is idempotent.
    if content and len(content) >= len(to_insert) and content[: len(to_insert)] == to_insert:
        content = to_insert + content[len(to_insert) :]
    else:
        content = to_insert + content

    save_file(file, content)


# -----------------------------------------------------------------------------


def remove(file, file_type, ft, style):
    lines = load_file(file)

    if file_type == ".py":
        content = []
        in_docstring = False
        for line in lines:
            if line.strip() == '"""' and not in_docstring:
                in_docstring = True
                continue
            if line.strip() == '"""' and in_docstring:
                in_docstring = False
                continue
            if not in_docstring:
                content.append(line)
    else:
        c = ft["comment"]
        content = [line for line in lines if not line.startswith(c + style["indicator"])]

    save_file(file, content)


# -----------------------------------------------------------------------------


DEFAULT_FT = {"comment": "#"}


def execute(flag, file, file_type_map, style):
    options = {"-v": show, "-m": edit, "-c": create, "-d": remove}

    file_type = "." + file.split(".")[-1]
    options[flag](file, file_type, file_type_map.get(file_type, DEFAULT_FT), style)


# -----------------------------------------------------------------------------


def main():
    file_type_map = {
        ".py": {"comment": None, "shebang": "#!/usr/bin/env python3"},
        ".sh": {"comment": "#", "shebang": "#! /bin/sh"},
        ".bash": {"comment": "#", "shebang": "#! /bin/bash"},
        ".rs": {"comment": "//", "shebang": None},
        ".md": {"comment": "[//]: # (", "shebang": None, "end": " )"},
    }

    style = {
        "author": "Ran# <ran.hash@proton.me>",
        "indicator": "+",  # Caution: changing this will break edit on files with old indicators
        "label_author": "Authors",
        "label_created": "Created",
        "label_revised": "Revised",
        "date_sep": "/",
        "time_sep": ":",
        "microsec": True,
        "microsec_sep": ".",
    }

    flag, file = read_input()
    execute(flag, file, file_type_map, style)


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()

# -----------------------------------------------------------------------------
