#!/usr/bin/env python3
# -----------------------------------------------------------------------------
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026-03-17
Revised: 2026-03-17
"""
# -----------------------------------------------------------------------------

from pathlib import Path

import pytest

from main import (
    create,
    edit,
    format_now,
    load_file,
    remove,
    save_file,
    show,
    split_first_line,
)

# -----------------------------------------------------------------------------
# FIXTURES
# -----------------------------------------------------------------------------

STYLE = {
    "author": "Test Author",
    "indicator": "+",
    "label_author": "Authors",
    "label_created": "Created",
    "label_revised": "Revised",
    "date_sep": "/",
    "time_sep": ":",
    "microsec": False,
    "microsec_sep": ".",
}

FILE_TYPE_MAP = {
    ".py": "#!/usr/bin/env python3",
    ".sh": "#! /bin/sh",
    ".rs": "//",
    ".md": ["[//]: # (", ")"],
}

PY_WITH_META = (
    '#!/usr/bin/env python3\n"""\nAuthors: Old\nCreated: 2020/01/01 00:00:00\n'
    'Revised: 2020/01/01 00:00:00\n"""\n\ndef foo():\n    pass\n'
)

SH_WITH_META = (
    "#! /bin/sh\n"
    "# ---------------------------------------------------------------------------\n"
    "#+ Authors: \tOld\n"
    "#+ Created: \t2020/01/01 00:00:00\n"
    "#+ Revised: \t2020/01/01 00:00:00\n"
    "# ---------------------------------------------------------------------------\n"
    "\necho hello\n"
)

MD_WITH_META = (
    "[//]: # ( --------------------------------------------------------------------------- )\n"
    "[//]: # (+  Authors: \tOld )\n"
    "[//]: # (+  Created: \t2020/01/01 00:00:00 )\n"
    "[//]: # (+  Revised: \t2020/01/01 00:00:00 )\n"
    "[//]: # ( --------------------------------------------------------------------------- )\n"
    "\n# Title\n"
)


@pytest.fixture
def tmp_py(tmp_path):
    f = tmp_path / "sample.py"
    f.write_text(PY_WITH_META, encoding="utf-8")
    return str(f)


@pytest.fixture
def tmp_sh(tmp_path):
    f = tmp_path / "sample.sh"
    f.write_text(SH_WITH_META, encoding="utf-8")
    return str(f)


@pytest.fixture
def tmp_md(tmp_path):
    f = tmp_path / "sample.md"
    f.write_text(MD_WITH_META, encoding="utf-8")
    return str(f)


@pytest.fixture
def tmp_empty_py(tmp_path):
    f = tmp_path / "empty.py"
    f.write_text("", encoding="utf-8")
    return str(f)


@pytest.fixture
def tmp_empty_sh(tmp_path):
    f = tmp_path / "empty.sh"
    f.write_text("", encoding="utf-8")
    return str(f)


@pytest.fixture
def tmp_empty_md(tmp_path):
    f = tmp_path / "empty.md"
    f.write_text("", encoding="utf-8")
    return str(f)


@pytest.fixture
def tmp_empty_txt(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_text("", encoding="utf-8")
    return str(f)


# -----------------------------------------------------------------------------
# save_file / load_file
# -----------------------------------------------------------------------------


def test_save_and_load_string(tmp_path):
    f = str(tmp_path / "out.txt")
    save_file(f, "hello world", encoding="utf-8")
    assert load_file(f, in_lines=False, encoding="utf-8") == "hello world"


def test_save_and_load_lines(tmp_path):
    f = str(tmp_path / "out.txt")
    save_file(f, ["line1", "line2", "line3"], encoding="utf-8")
    assert load_file(f, in_lines=True, encoding="utf-8") == ["line1", "line2", "line3"]


def test_save_creates_missing_dirs(tmp_path):
    f = str(tmp_path / "a" / "b" / "out.txt")
    save_file(f, "data", encoding="utf-8")
    assert Path(f).exists()


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_file(str(tmp_path / "nope.txt"))


def test_save_empty_list(tmp_path):
    f = str(tmp_path / "out.txt")
    save_file(f, [], encoding="utf-8")
    assert load_file(f, in_lines=True, encoding="utf-8") == []


def test_load_no_bom(tmp_path):
    """Files saved with utf-8 must not have a BOM prefix on the first line."""
    f = str(tmp_path / "out.txt")
    save_file(f, ["hello"], encoding="utf-8")
    lines = load_file(f, in_lines=True, encoding="utf-8")
    assert lines[0] == "hello"
    assert not lines[0].startswith("\ufeff")


# -----------------------------------------------------------------------------
# split_first_line
# -----------------------------------------------------------------------------


def test_split_first_line_string():
    sym, end = split_first_line("#! /bin/sh")
    assert sym == "#! /bin/sh"
    assert end == ""


def test_split_first_line_list():
    sym, end = split_first_line(["[//]: # (", ")"])
    assert sym == "[//]: # ("
    assert end == " )"


# -----------------------------------------------------------------------------
# format_now
# -----------------------------------------------------------------------------


def test_format_now_no_microsec():
    result = format_now({**STYLE, "microsec": False})
    assert len(result) == 19
    assert result[4] == "/"
    assert result[7] == "/"
    assert result[13] == ":"
    assert result[16] == ":"


def test_format_now_with_microsec():
    result = format_now({**STYLE, "microsec": True, "microsec_sep": "."})
    assert len(result) == 26
    assert result[19] == "."


def test_format_now_custom_seps():
    result = format_now({**STYLE, "microsec": False, "date_sep": "-", "time_sep": "."})
    assert result[4] == "-"
    assert result[13] == "."


# -----------------------------------------------------------------------------
# show
# -----------------------------------------------------------------------------


def test_show_py_prints_only_metadata_lines(tmp_py, capsys):
    show(tmp_py, ".py", FILE_TYPE_MAP[".py"], STYLE)
    out = capsys.readouterr().out.splitlines()
    assert any("Authors: Old" in line for line in out)
    assert any("Created:" in line for line in out)
    assert any("Revised:" in line for line in out)
    # code outside docstring must not appear
    assert not any("def foo" in line for line in out)
    assert not any("pass" in line for line in out)


def test_show_sh_prints_only_metadata_lines(tmp_sh, capsys):
    show(tmp_sh, ".sh", FILE_TYPE_MAP[".sh"], STYLE)
    out = capsys.readouterr().out.splitlines()
    assert any("Authors" in line for line in out)
    assert any("Created" in line for line in out)
    assert any("Revised" in line for line in out)
    # non-metadata lines must not appear
    assert not any("echo hello" in line for line in out)
    assert not any("# ---" in line for line in out)


def test_show_md_prints_only_metadata_lines(tmp_md, capsys):
    show(tmp_md, ".md", FILE_TYPE_MAP[".md"], STYLE)
    out = capsys.readouterr().out.splitlines()
    assert any("Authors" in line for line in out)
    assert not any("# Title" in line for line in out)


def test_show_py_no_metadata_prints_nothing(tmp_empty_py, capsys):
    show(tmp_empty_py, ".py", FILE_TYPE_MAP[".py"], STYLE)
    assert capsys.readouterr().out == ""


def test_show_sh_no_metadata_prints_nothing(tmp_empty_sh, capsys):
    show(tmp_empty_sh, ".sh", FILE_TYPE_MAP[".sh"], STYLE)
    assert capsys.readouterr().out == ""


# -----------------------------------------------------------------------------
# edit
# -----------------------------------------------------------------------------


def test_edit_py_revised_changes(tmp_py):
    before = load_file(tmp_py, encoding="utf-8")
    revised_before = next(line for line in before if line.startswith("Revised:"))

    edit(tmp_py, ".py", FILE_TYPE_MAP[".py"], STYLE)

    after = load_file(tmp_py, encoding="utf-8")
    revised_after = next(line for line in after if line.startswith("Revised:"))
    assert revised_after != revised_before


def test_edit_py_author_and_created_unchanged(tmp_py):
    before = load_file(tmp_py, encoding="utf-8")
    author_before = next(line for line in before if line.startswith("Authors:"))
    created_before = next(line for line in before if line.startswith("Created:"))

    edit(tmp_py, ".py", FILE_TYPE_MAP[".py"], STYLE)

    after = load_file(tmp_py, encoding="utf-8")
    assert next(line for line in after if line.startswith("Authors:")) == author_before
    assert next(line for line in after if line.startswith("Created:")) == created_before


def test_edit_py_preserves_code(tmp_py):
    edit(tmp_py, ".py", FILE_TYPE_MAP[".py"], STYLE)
    after = load_file(tmp_py, encoding="utf-8")
    assert any("def foo():" in line for line in after)


def test_edit_sh_revised_changes(tmp_sh):
    before = load_file(tmp_sh, encoding="utf-8")
    revised_before = next(line for line in before if "#+ Revised:" in line)

    edit(tmp_sh, ".sh", FILE_TYPE_MAP[".sh"], STYLE)

    after = load_file(tmp_sh, encoding="utf-8")
    revised_after = next(line for line in after if "#+ Revised:" in line)
    assert revised_after != revised_before


def test_edit_sh_author_and_created_unchanged(tmp_sh):
    before = load_file(tmp_sh, encoding="utf-8")
    author_before = next(line for line in before if "#+ Authors:" in line)
    created_before = next(line for line in before if "#+ Created:" in line)

    edit(tmp_sh, ".sh", FILE_TYPE_MAP[".sh"], STYLE)

    after = load_file(tmp_sh, encoding="utf-8")
    assert next(line for line in after if "#+ Authors:" in line) == author_before
    assert next(line for line in after if "#+ Created:" in line) == created_before


def test_edit_sh_preserves_code(tmp_sh):
    edit(tmp_sh, ".sh", FILE_TYPE_MAP[".sh"], STYLE)
    after = load_file(tmp_sh, encoding="utf-8")
    assert any("echo hello" in line for line in after)


def test_edit_py_no_metadata_is_noop(tmp_empty_py):
    before = load_file(tmp_empty_py, encoding="utf-8")
    edit(tmp_empty_py, ".py", FILE_TYPE_MAP[".py"], STYLE)
    after = load_file(tmp_empty_py, encoding="utf-8")
    assert after == before


def test_edit_sh_no_metadata_is_noop(tmp_empty_sh):
    before = load_file(tmp_empty_sh, encoding="utf-8")
    edit(tmp_empty_sh, ".sh", FILE_TYPE_MAP[".sh"], STYLE)
    after = load_file(tmp_empty_sh, encoding="utf-8")
    assert after == before


# -----------------------------------------------------------------------------
# create
# -----------------------------------------------------------------------------


def test_create_py_structure(tmp_empty_py):
    create(tmp_empty_py, ".py", FILE_TYPE_MAP[".py"], STYLE)
    lines = load_file(tmp_empty_py, encoding="utf-8")
    assert lines[0] == "#!/usr/bin/env python3"
    assert lines[1] == '"""'
    assert lines[2].startswith("Authors:")
    assert lines[3].startswith("Created:")
    assert lines[4].startswith("Revised:")
    assert lines[5] == '"""'


def test_create_py_contains_author(tmp_empty_py):
    create(tmp_empty_py, ".py", FILE_TYPE_MAP[".py"], STYLE)
    lines = load_file(tmp_empty_py, encoding="utf-8")
    assert any("Test Author" in line for line in lines)


def test_create_sh_structure(tmp_empty_sh):
    create(tmp_empty_sh, ".sh", FILE_TYPE_MAP[".sh"], STYLE)
    lines = load_file(tmp_empty_sh, encoding="utf-8")
    assert lines[0] == "#! /bin/sh"
    assert lines[1].startswith("# -")
    assert "#+ Authors:" in lines[2]
    assert "#+ Created:" in lines[3]
    assert "#+ Revised:" in lines[4]
    assert lines[5].startswith("# -")


def test_create_sh_contains_author(tmp_empty_sh):
    create(tmp_empty_sh, ".sh", FILE_TYPE_MAP[".sh"], STYLE)
    lines = load_file(tmp_empty_sh, encoding="utf-8")
    assert any("Test Author" in line for line in lines)


def test_create_py_preserves_existing_code(tmp_py):
    create(tmp_py, ".py", FILE_TYPE_MAP[".py"], STYLE)
    lines = load_file(tmp_py, encoding="utf-8")
    assert any("def foo():" in line for line in lines)


def test_create_sh_preserves_existing_code(tmp_sh):
    create(tmp_sh, ".sh", FILE_TYPE_MAP[".sh"], STYLE)
    lines = load_file(tmp_sh, encoding="utf-8")
    assert any("echo hello" in line for line in lines)


def test_create_py_idempotent(tmp_py):
    """Calling create twice must not double the header."""
    create(tmp_py, ".py", FILE_TYPE_MAP[".py"], STYLE)
    lines_once = load_file(tmp_py, encoding="utf-8")

    create(tmp_py, ".py", FILE_TYPE_MAP[".py"], STYLE)
    lines_twice = load_file(tmp_py, encoding="utf-8")

    assert lines_once.count('"""') == lines_twice.count('"""')


def test_create_sh_idempotent(tmp_sh):
    """Calling create twice must not double the header."""
    create(tmp_sh, ".sh", FILE_TYPE_MAP[".sh"], STYLE)
    lines_once = load_file(tmp_sh, encoding="utf-8")

    create(tmp_sh, ".sh", FILE_TYPE_MAP[".sh"], STYLE)
    lines_twice = load_file(tmp_sh, encoding="utf-8")

    count_once = sum(1 for line in lines_once if "#+ Authors:" in line)
    count_twice = sum(1 for line in lines_twice if "#+ Authors:" in line)
    assert count_once == count_twice


def test_create_md_structure(tmp_empty_md):
    create(tmp_empty_md, ".md", FILE_TYPE_MAP[".md"], STYLE)
    lines = load_file(tmp_empty_md, encoding="utf-8")
    assert any("Authors" in line for line in lines)
    assert any("Created" in line for line in lines)
    assert any("Revised" in line for line in lines)
    # md lines must use the [//]: # (...) format
    meta_lines = [line for line in lines if "Authors" in line or "Created" in line or "Revised" in line]
    assert all(line.startswith("[//]: # (") for line in meta_lines)


def test_create_fallback_txt(tmp_empty_txt):
    """Unknown file types fall back to # comment style."""
    create(tmp_empty_txt, ".txt", "#", STYLE)
    lines = load_file(tmp_empty_txt, encoding="utf-8")
    assert any("#+ Authors:" in line for line in lines)


# -----------------------------------------------------------------------------
# remove
# -----------------------------------------------------------------------------


def test_remove_py_strips_docstring(tmp_py):
    remove(tmp_py, ".py", FILE_TYPE_MAP[".py"], STYLE)
    lines = load_file(tmp_py, encoding="utf-8")
    assert '"""' not in lines
    assert not any("Authors:" in line for line in lines)
    assert not any("Created:" in line for line in lines)
    assert not any("Revised:" in line for line in lines)


def test_remove_py_keeps_shebang_and_code(tmp_py):
    remove(tmp_py, ".py", FILE_TYPE_MAP[".py"], STYLE)
    lines = load_file(tmp_py, encoding="utf-8")
    assert lines[0] == "#!/usr/bin/env python3"
    assert any("def foo():" in line for line in lines)


def test_remove_sh_strips_metadata_lines(tmp_sh):
    remove(tmp_sh, ".sh", FILE_TYPE_MAP[".sh"], STYLE)
    lines = load_file(tmp_sh, encoding="utf-8")
    assert not any(line.startswith("#+ ") for line in lines)
    assert not any("Authors" in line for line in lines)


def test_remove_sh_keeps_code(tmp_sh):
    remove(tmp_sh, ".sh", FILE_TYPE_MAP[".sh"], STYLE)
    lines = load_file(tmp_sh, encoding="utf-8")
    assert any("echo hello" in line for line in lines)


def test_remove_py_no_metadata_is_noop(tmp_empty_py):
    remove(tmp_empty_py, ".py", FILE_TYPE_MAP[".py"], STYLE)
    assert load_file(tmp_empty_py, encoding="utf-8") == []


def test_remove_sh_no_metadata_is_noop(tmp_empty_sh):
    before = load_file(tmp_empty_sh, encoding="utf-8")
    remove(tmp_empty_sh, ".sh", FILE_TYPE_MAP[".sh"], STYLE)
    assert load_file(tmp_empty_sh, encoding="utf-8") == before


# -----------------------------------------------------------------------------
# round-trip: create -> show -> edit -> remove
# -----------------------------------------------------------------------------


def test_roundtrip_py(tmp_empty_py, capsys):
    style = {**STYLE, "microsec": True}
    create(tmp_empty_py, ".py", FILE_TYPE_MAP[".py"], style)

    show(tmp_empty_py, ".py", FILE_TYPE_MAP[".py"], STYLE)
    assert "Authors:" in capsys.readouterr().out

    created_before = next(
        line for line in load_file(tmp_empty_py, encoding="utf-8") if line.startswith("Created:")
    )
    revised_before = next(
        line for line in load_file(tmp_empty_py, encoding="utf-8") if line.startswith("Revised:")
    )

    edit(tmp_empty_py, ".py", FILE_TYPE_MAP[".py"], style)
    after_edit = load_file(tmp_empty_py, encoding="utf-8")
    assert next(line for line in after_edit if line.startswith("Created:")) == created_before
    assert next(line for line in after_edit if line.startswith("Revised:")) != revised_before

    remove(tmp_empty_py, ".py", FILE_TYPE_MAP[".py"], STYLE)
    after_remove = load_file(tmp_empty_py, encoding="utf-8")
    assert not any("Authors:" in line for line in after_remove)
    assert '"""' not in after_remove


def test_roundtrip_sh(tmp_empty_sh, capsys):
    style = {**STYLE, "microsec": True}
    create(tmp_empty_sh, ".sh", FILE_TYPE_MAP[".sh"], style)

    show(tmp_empty_sh, ".sh", FILE_TYPE_MAP[".sh"], style)
    assert "Authors" in capsys.readouterr().out

    revised_before = next(
        line for line in load_file(tmp_empty_sh, encoding="utf-8") if "#+ Revised:" in line
    )

    edit(tmp_empty_sh, ".sh", FILE_TYPE_MAP[".sh"], style)
    after_edit = load_file(tmp_empty_sh, encoding="utf-8")
    assert next(line for line in after_edit if "#+ Revised:" in line) != revised_before

    remove(tmp_empty_sh, ".sh", FILE_TYPE_MAP[".sh"], STYLE)
    after_remove = load_file(tmp_empty_sh, encoding="utf-8")
    assert not any(line.startswith("#+ ") for line in after_remove)
