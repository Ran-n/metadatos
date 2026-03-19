#!/usr/bin/env python3
# -----------------------------------------------------------------------------
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026-03-17
Revised: 2026/03/19 09:06:25.772825
"""
# -----------------------------------------------------------------------------

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from main import (
    create,
    edit,
    execute,
    format_now,
    load_file,
    read_input,
    remove,
    save_file,
    show,
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

FT_PY = {"comment": None, "shebang": "#!/usr/bin/env python3"}
FT_SH = {"comment": "#", "shebang": "#! /bin/sh"}
FT_RS = {"comment": "//", "shebang": None}
FT_MD = {"comment": "[//]: # (", "shebang": None, "end": " )"}
FT_TXT = {"comment": "#"}

FILE_TYPE_MAP = {
    ".py": FT_PY,
    ".sh": FT_SH,
    ".rs": FT_RS,
    ".md": FT_MD,
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

RS_WITH_META = (
    "// ---------------------------------------------------------------------------\n"
    "//+ Authors: \tOld\n"
    "//+ Created: \t2020/01/01 00:00:00\n"
    "//+ Revised: \t2020/01/01 00:00:00\n"
    "// ---------------------------------------------------------------------------\n"
    "\nfn main() {}\n"
)

MD_WITH_META = (
    "[//]: # ( --------------------------------------------------------------------------- )\n"
    "[//]: # (+ Authors: \tOld )\n"
    "[//]: # (+ Created: \t2020/01/01 00:00:00 )\n"
    "[//]: # (+ Revised: \t2020/01/01 00:00:00 )\n"
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
def tmp_rs(tmp_path):
    f = tmp_path / "sample.rs"
    f.write_text(RS_WITH_META, encoding="utf-8")
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
def tmp_empty_rs(tmp_path):
    f = tmp_path / "empty.rs"
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
# read_input
# -----------------------------------------------------------------------------


def test_read_input_no_args_exits(capsys):
    with patch.object(sys, "argv", ["main.py"]), pytest.raises(SystemExit):
        read_input()
    assert "Help" in capsys.readouterr().out


@pytest.mark.parametrize("flag", ["-h", "?", "-?", "--help"])
def test_read_input_help_flags_exit(flag, capsys):
    with patch.object(sys, "argv", ["main.py", flag]), pytest.raises(SystemExit):
        read_input()
    assert "Help" in capsys.readouterr().out


def test_read_input_unknown_flag_exits(capsys):
    with patch.object(sys, "argv", ["main.py", "-x", "file.py"]), pytest.raises(SystemExit):
        read_input()
    assert "Help" in capsys.readouterr().out


def test_read_input_missing_file_exits(capsys):
    with patch.object(sys, "argv", ["main.py", "-v"]), pytest.raises(SystemExit):
        read_input()
    out = capsys.readouterr().out
    assert "ERROR" in out


@pytest.mark.parametrize("flag", ["-v", "-m", "-c", "-d"])
def test_read_input_valid_flags_return(flag):
    with patch.object(sys, "argv", ["main.py", flag, "file.py"]):
        result_flag, result_file = read_input()
    assert result_flag == flag
    assert result_file == "file.py"


# -----------------------------------------------------------------------------
# show
# -----------------------------------------------------------------------------


def test_show_py_prints_only_metadata_lines(tmp_py, capsys):
    show(tmp_py, ".py", FT_PY, STYLE)
    out = capsys.readouterr().out.splitlines()
    assert any("Authors: Old" in line for line in out)
    assert any("Created:" in line for line in out)
    assert any("Revised:" in line for line in out)
    assert not any("def foo" in line for line in out)
    assert not any("pass" in line for line in out)


def test_show_py_no_metadata_prints_nothing(tmp_empty_py, capsys):
    show(tmp_empty_py, ".py", FT_PY, STYLE)
    assert capsys.readouterr().out == ""


def test_show_sh_prints_only_metadata_lines(tmp_sh, capsys):
    show(tmp_sh, ".sh", FT_SH, STYLE)
    out = capsys.readouterr().out.splitlines()
    assert any("Authors" in line for line in out)
    assert any("Created" in line for line in out)
    assert any("Revised" in line for line in out)
    assert not any("echo hello" in line for line in out)
    assert not any("# ---" in line for line in out)


def test_show_sh_no_metadata_prints_nothing(tmp_empty_sh, capsys):
    show(tmp_empty_sh, ".sh", FT_SH, STYLE)
    assert capsys.readouterr().out == ""


def test_show_rs_prints_only_metadata_lines(tmp_rs, capsys):
    show(tmp_rs, ".rs", FT_RS, STYLE)
    out = capsys.readouterr().out.splitlines()
    assert any("Authors" in line for line in out)
    assert not any("fn main" in line for line in out)


def test_show_md_prints_only_metadata_lines(tmp_md, capsys):
    show(tmp_md, ".md", FT_MD, STYLE)
    out = capsys.readouterr().out.splitlines()
    assert any("Authors" in line for line in out)
    assert not any("# Title" in line for line in out)


def test_show_md_no_metadata_prints_nothing(tmp_empty_md, capsys):
    show(tmp_empty_md, ".md", FT_MD, STYLE)
    assert capsys.readouterr().out == ""


# -----------------------------------------------------------------------------
# edit
# -----------------------------------------------------------------------------


def test_edit_py_revised_changes(tmp_py):
    before = load_file(tmp_py, encoding="utf-8")
    revised_before = next(line for line in before if line.startswith("Revised:"))
    edit(tmp_py, ".py", FT_PY, STYLE)
    after = load_file(tmp_py, encoding="utf-8")
    revised_after = next(line for line in after if line.startswith("Revised:"))
    assert revised_after != revised_before


def test_edit_py_author_and_created_unchanged(tmp_py):
    before = load_file(tmp_py, encoding="utf-8")
    author_before = next(line for line in before if line.startswith("Authors:"))
    created_before = next(line for line in before if line.startswith("Created:"))
    edit(tmp_py, ".py", FT_PY, STYLE)
    after = load_file(tmp_py, encoding="utf-8")
    assert next(line for line in after if line.startswith("Authors:")) == author_before
    assert next(line for line in after if line.startswith("Created:")) == created_before


def test_edit_py_preserves_code(tmp_py):
    edit(tmp_py, ".py", FT_PY, STYLE)
    assert any("def foo():" in line for line in load_file(tmp_py, encoding="utf-8"))


def test_edit_py_no_metadata_is_noop(tmp_empty_py):
    before = load_file(tmp_empty_py, encoding="utf-8")
    edit(tmp_empty_py, ".py", FT_PY, STYLE)
    assert load_file(tmp_empty_py, encoding="utf-8") == before


def test_edit_sh_revised_changes(tmp_sh):
    before = load_file(tmp_sh, encoding="utf-8")
    revised_before = next(line for line in before if "#+ Revised:" in line)
    edit(tmp_sh, ".sh", FT_SH, STYLE)
    after = load_file(tmp_sh, encoding="utf-8")
    revised_after = next(line for line in after if "#+ Revised:" in line)
    assert revised_after != revised_before


def test_edit_sh_author_and_created_unchanged(tmp_sh):
    before = load_file(tmp_sh, encoding="utf-8")
    author_before = next(line for line in before if "#+ Authors:" in line)
    created_before = next(line for line in before if "#+ Created:" in line)
    edit(tmp_sh, ".sh", FT_SH, STYLE)
    after = load_file(tmp_sh, encoding="utf-8")
    assert next(line for line in after if "#+ Authors:" in line) == author_before
    assert next(line for line in after if "#+ Created:" in line) == created_before


def test_edit_sh_preserves_code(tmp_sh):
    edit(tmp_sh, ".sh", FT_SH, STYLE)
    assert any("echo hello" in line for line in load_file(tmp_sh, encoding="utf-8"))


def test_edit_sh_no_metadata_is_noop(tmp_empty_sh):
    before = load_file(tmp_empty_sh, encoding="utf-8")
    edit(tmp_empty_sh, ".sh", FT_SH, STYLE)
    assert load_file(tmp_empty_sh, encoding="utf-8") == before


def test_edit_rs_revised_changes(tmp_rs):
    """Rust uses // comment with no end closer."""
    before = load_file(tmp_rs, encoding="utf-8")
    revised_before = next(line for line in before if "//+ Revised:" in line)
    edit(tmp_rs, ".rs", FT_RS, STYLE)
    after = load_file(tmp_rs, encoding="utf-8")
    revised_after = next(line for line in after if "//+ Revised:" in line)
    assert revised_after != revised_before


def test_edit_rs_revised_has_no_trailing_end(tmp_rs):
    """Rust ft has no 'end' key — revised line must not gain a trailing closer."""
    edit(tmp_rs, ".rs", FT_RS, STYLE)
    after = load_file(tmp_rs, encoding="utf-8")
    revised = next(line for line in after if "//+ Revised:" in line)
    assert not revised.endswith(" )")


def test_edit_md_revised_changes(tmp_md):
    """Markdown uses end closer ' )'."""
    before = load_file(tmp_md, encoding="utf-8")
    revised_before = next(line for line in before if "Revised:" in line)
    edit(tmp_md, ".md", FT_MD, STYLE)
    after = load_file(tmp_md, encoding="utf-8")
    revised_after = next(line for line in after if "Revised:" in line)
    assert revised_after != revised_before


def test_edit_md_revised_ends_with_closer(tmp_md):
    """Markdown revised line must retain the ' )' end closer."""
    edit(tmp_md, ".md", FT_MD, STYLE)
    after = load_file(tmp_md, encoding="utf-8")
    revised = next(line for line in after if "Revised:" in line)
    assert revised.endswith(" )")


# -----------------------------------------------------------------------------
# create
# -----------------------------------------------------------------------------


def test_create_py_structure(tmp_empty_py):
    create(tmp_empty_py, ".py", FT_PY, STYLE)
    lines = load_file(tmp_empty_py, encoding="utf-8")
    assert lines[0] == "#!/usr/bin/env python3"
    assert lines[1] == '"""'
    assert lines[2].startswith("Authors:")
    assert lines[3].startswith("Created:")
    assert lines[4].startswith("Revised:")
    assert lines[5] == '"""'


def test_create_py_contains_author(tmp_empty_py):
    create(tmp_empty_py, ".py", FT_PY, STYLE)
    assert any("Test Author" in line for line in load_file(tmp_empty_py, encoding="utf-8"))


def test_create_py_preserves_existing_code(tmp_py):
    create(tmp_py, ".py", FT_PY, STYLE)
    assert any("def foo():" in line for line in load_file(tmp_py, encoding="utf-8"))


def test_create_py_idempotent(tmp_py):
    create(tmp_py, ".py", FT_PY, STYLE)
    lines_once = load_file(tmp_py, encoding="utf-8")
    create(tmp_py, ".py", FT_PY, STYLE)
    lines_twice = load_file(tmp_py, encoding="utf-8")
    assert lines_once.count('"""') == lines_twice.count('"""')


def test_create_sh_structure(tmp_empty_sh):
    create(tmp_empty_sh, ".sh", FT_SH, STYLE)
    lines = load_file(tmp_empty_sh, encoding="utf-8")
    assert lines[0] == "#! /bin/sh"
    assert lines[1].startswith("# -")
    assert "#+ Authors:" in lines[2]
    assert "#+ Created:" in lines[3]
    assert "#+ Revised:" in lines[4]
    assert lines[5].startswith("# -")


def test_create_sh_contains_author(tmp_empty_sh):
    create(tmp_empty_sh, ".sh", FT_SH, STYLE)
    assert any("Test Author" in line for line in load_file(tmp_empty_sh, encoding="utf-8"))


def test_create_sh_preserves_existing_code(tmp_sh):
    create(tmp_sh, ".sh", FT_SH, STYLE)
    assert any("echo hello" in line for line in load_file(tmp_sh, encoding="utf-8"))


def test_create_sh_idempotent(tmp_sh):
    create(tmp_sh, ".sh", FT_SH, STYLE)
    lines_once = load_file(tmp_sh, encoding="utf-8")
    create(tmp_sh, ".sh", FT_SH, STYLE)
    lines_twice = load_file(tmp_sh, encoding="utf-8")
    count_once = sum(1 for line in lines_once if "#+ Authors:" in line)
    count_twice = sum(1 for line in lines_twice if "#+ Authors:" in line)
    assert count_once == count_twice


def test_create_rs_no_shebang(tmp_empty_rs):
    """Rust has shebang: None — first line must be the separator, not a shebang."""
    create(tmp_empty_rs, ".rs", FT_RS, STYLE)
    lines = load_file(tmp_empty_rs, encoding="utf-8")
    assert lines[0].startswith("// -")
    assert "//+ Authors:" in lines[1]
    assert "//+ Created:" in lines[2]
    assert "//+ Revised:" in lines[3]
    assert lines[4].startswith("// -")


def test_create_rs_preserves_existing_code(tmp_rs):
    create(tmp_rs, ".rs", FT_RS, STYLE)
    assert any("fn main" in line for line in load_file(tmp_rs, encoding="utf-8"))


def test_create_rs_idempotent(tmp_rs):
    create(tmp_rs, ".rs", FT_RS, STYLE)
    lines_once = load_file(tmp_rs, encoding="utf-8")
    create(tmp_rs, ".rs", FT_RS, STYLE)
    lines_twice = load_file(tmp_rs, encoding="utf-8")
    count_once = sum(1 for line in lines_once if "//+ Authors:" in line)
    count_twice = sum(1 for line in lines_twice if "//+ Authors:" in line)
    assert count_once == count_twice


def test_create_md_structure(tmp_empty_md):
    create(tmp_empty_md, ".md", FT_MD, STYLE)
    lines = load_file(tmp_empty_md, encoding="utf-8")
    meta_lines = [line for line in lines if "Authors" in line or "Created" in line or "Revised" in line]
    assert meta_lines
    assert all(line.startswith("[//]: # (") for line in meta_lines)
    assert all(line.endswith(" )") for line in meta_lines)


def test_create_md_no_shebang(tmp_empty_md):
    """Markdown has shebang: None — no shebang line must appear."""
    create(tmp_empty_md, ".md", FT_MD, STYLE)
    lines = load_file(tmp_empty_md, encoding="utf-8")
    assert not any(line.startswith("#!") for line in lines)


def test_create_md_preserves_existing_content(tmp_md):
    create(tmp_md, ".md", FT_MD, STYLE)
    assert any("# Title" in line for line in load_file(tmp_md, encoding="utf-8"))


def test_create_fallback_no_shebang(tmp_empty_txt):
    """Fallback ft has no shebang key — must not crash and must not prepend a shebang."""
    create(tmp_empty_txt, ".txt", FT_TXT, STYLE)
    lines = load_file(tmp_empty_txt, encoding="utf-8")
    assert any("#+ Authors:" in line for line in lines)
    assert not any(line.startswith("#!") for line in lines)


def test_create_body_shorter_than_header_not_lost(tmp_path):
    """A file whose body is shorter than the header must not have its body silently dropped."""
    f = tmp_path / "tiny.sh"
    f.write_text("echo hi\n", encoding="utf-8")
    create(str(f), ".sh", FT_SH, STYLE)
    lines = load_file(str(f), encoding="utf-8")
    assert any("echo hi" in line for line in lines)


# -----------------------------------------------------------------------------
# remove
# -----------------------------------------------------------------------------


def test_remove_py_strips_docstring(tmp_py):
    remove(tmp_py, ".py", FT_PY, STYLE)
    lines = load_file(tmp_py, encoding="utf-8")
    assert '"""' not in lines
    assert not any("Authors:" in line for line in lines)
    assert not any("Created:" in line for line in lines)
    assert not any("Revised:" in line for line in lines)


def test_remove_py_keeps_shebang_and_code(tmp_py):
    remove(tmp_py, ".py", FT_PY, STYLE)
    lines = load_file(tmp_py, encoding="utf-8")
    assert lines[0] == "#!/usr/bin/env python3"
    assert any("def foo():" in line for line in lines)


def test_remove_py_no_metadata_is_noop(tmp_empty_py):
    remove(tmp_empty_py, ".py", FT_PY, STYLE)
    assert load_file(tmp_empty_py, encoding="utf-8") == []


def test_remove_sh_strips_metadata_lines(tmp_sh):
    remove(tmp_sh, ".sh", FT_SH, STYLE)
    lines = load_file(tmp_sh, encoding="utf-8")
    assert not any(line.startswith("#+ ") for line in lines)
    assert not any("Authors" in line for line in lines)


def test_remove_sh_keeps_code(tmp_sh):
    remove(tmp_sh, ".sh", FT_SH, STYLE)
    assert any("echo hello" in line for line in load_file(tmp_sh, encoding="utf-8"))


def test_remove_sh_no_metadata_is_noop(tmp_empty_sh):
    before = load_file(tmp_empty_sh, encoding="utf-8")
    remove(tmp_empty_sh, ".sh", FT_SH, STYLE)
    assert load_file(tmp_empty_sh, encoding="utf-8") == before


def test_remove_rs_strips_metadata_lines(tmp_rs):
    remove(tmp_rs, ".rs", FT_RS, STYLE)
    lines = load_file(tmp_rs, encoding="utf-8")
    assert not any(line.startswith("//+ ") for line in lines)
    assert not any("Authors" in line for line in lines)


def test_remove_rs_keeps_code(tmp_rs):
    remove(tmp_rs, ".rs", FT_RS, STYLE)
    assert any("fn main" in line for line in load_file(tmp_rs, encoding="utf-8"))


def test_remove_md_strips_metadata_lines(tmp_md):
    remove(tmp_md, ".md", FT_MD, STYLE)
    lines = load_file(tmp_md, encoding="utf-8")
    assert not any("Authors" in line for line in lines)
    assert not any("Revised" in line for line in lines)


def test_remove_md_keeps_content(tmp_md):
    remove(tmp_md, ".md", FT_MD, STYLE)
    assert any("# Title" in line for line in load_file(tmp_md, encoding="utf-8"))


# -----------------------------------------------------------------------------
# execute
# -----------------------------------------------------------------------------


def test_execute_uses_default_ft_for_unknown_extension(tmp_path, capsys):
    """Files with unknown extensions fall back to DEFAULT_FT (# comment style)."""
    f = tmp_path / "notes.xyz"
    f.write_text("", encoding="utf-8")
    file_type_map = dict(FILE_TYPE_MAP)
    execute("-c", str(f), file_type_map, STYLE)
    lines = load_file(str(f), encoding="utf-8")
    assert any("#+ Authors:" in line for line in lines)


def test_execute_dispatches_show(tmp_py, capsys):
    execute("-v", tmp_py, FILE_TYPE_MAP, STYLE)
    assert "Authors" in capsys.readouterr().out


def test_execute_dispatches_edit(tmp_py):
    before = load_file(tmp_py, encoding="utf-8")
    revised_before = next(line for line in before if line.startswith("Revised:"))
    execute("-m", tmp_py, FILE_TYPE_MAP, STYLE)
    after = load_file(tmp_py, encoding="utf-8")
    revised_after = next(line for line in after if line.startswith("Revised:"))
    assert revised_after != revised_before


def test_execute_dispatches_create(tmp_empty_py):
    execute("-c", tmp_empty_py, FILE_TYPE_MAP, STYLE)
    assert any('"""' in line for line in load_file(tmp_empty_py, encoding="utf-8"))


def test_execute_dispatches_remove(tmp_py):
    execute("-d", tmp_py, FILE_TYPE_MAP, STYLE)
    assert not any("Authors:" in line for line in load_file(tmp_py, encoding="utf-8"))


# -----------------------------------------------------------------------------
# round-trip: create -> show -> edit -> remove
# -----------------------------------------------------------------------------


def test_roundtrip_py(tmp_empty_py, capsys):
    style = {**STYLE, "microsec": True}
    create(tmp_empty_py, ".py", FT_PY, style)

    show(tmp_empty_py, ".py", FT_PY, style)
    assert "Authors:" in capsys.readouterr().out

    created_before = next(line for line in load_file(tmp_empty_py, encoding="utf-8") if line.startswith("Created:"))
    revised_before = next(line for line in load_file(tmp_empty_py, encoding="utf-8") if line.startswith("Revised:"))

    edit(tmp_empty_py, ".py", FT_PY, style)
    after_edit = load_file(tmp_empty_py, encoding="utf-8")
    assert next(line for line in after_edit if line.startswith("Created:")) == created_before
    assert next(line for line in after_edit if line.startswith("Revised:")) != revised_before

    remove(tmp_empty_py, ".py", FT_PY, style)
    after_remove = load_file(tmp_empty_py, encoding="utf-8")
    assert not any("Authors:" in line for line in after_remove)
    assert '"""' not in after_remove


def test_roundtrip_sh(tmp_empty_sh, capsys):
    style = {**STYLE, "microsec": True}
    create(tmp_empty_sh, ".sh", FT_SH, style)

    show(tmp_empty_sh, ".sh", FT_SH, style)
    assert "Authors" in capsys.readouterr().out

    revised_before = next(line for line in load_file(tmp_empty_sh, encoding="utf-8") if "#+ Revised:" in line)

    edit(tmp_empty_sh, ".sh", FT_SH, style)
    after_edit = load_file(tmp_empty_sh, encoding="utf-8")
    assert next(line for line in after_edit if "#+ Revised:" in line) != revised_before

    remove(tmp_empty_sh, ".sh", FT_SH, style)
    after_remove = load_file(tmp_empty_sh, encoding="utf-8")
    assert not any(line.startswith("#+ ") for line in after_remove)


def test_roundtrip_rs(tmp_empty_rs, capsys):
    style = {**STYLE, "microsec": True}
    create(tmp_empty_rs, ".rs", FT_RS, style)

    show(tmp_empty_rs, ".rs", FT_RS, style)
    assert "Authors" in capsys.readouterr().out

    revised_before = next(line for line in load_file(tmp_empty_rs, encoding="utf-8") if "//+ Revised:" in line)

    edit(tmp_empty_rs, ".rs", FT_RS, style)
    after_edit = load_file(tmp_empty_rs, encoding="utf-8")
    assert next(line for line in after_edit if "//+ Revised:" in line) != revised_before

    remove(tmp_empty_rs, ".rs", FT_RS, style)
    after_remove = load_file(tmp_empty_rs, encoding="utf-8")
    assert not any(line.startswith("//+ ") for line in after_remove)


def test_roundtrip_md(tmp_empty_md, capsys):
    style = {**STYLE, "microsec": True}
    create(tmp_empty_md, ".md", FT_MD, style)

    show(tmp_empty_md, ".md", FT_MD, style)
    assert "Authors" in capsys.readouterr().out

    revised_before = next(line for line in load_file(tmp_empty_md, encoding="utf-8") if "Revised:" in line)

    edit(tmp_empty_md, ".md", FT_MD, style)
    after_edit = load_file(tmp_empty_md, encoding="utf-8")
    revised_after = next(line for line in after_edit if "Revised:" in line)
    assert revised_after != revised_before
    assert revised_after.endswith(" )")

    remove(tmp_empty_md, ".md", FT_MD, style)
    after_remove = load_file(tmp_empty_md, encoding="utf-8")
    assert not any("Authors" in line for line in after_remove)
