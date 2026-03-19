[//]: # ( --------------------------------------------------------------------------- )
[//]: # (+  Authors: 	Ran# <ran.hash@proton.me> )
[//]: # (+  Created: 	2022/10/30 10:37:41.000000 )
[//]: # (+  Revised: 	2026/03/17 10:00:00.000000 )
[//]: # ( --------------------------------------------------------------------------- )

# metadatos

A CLI tool to create, view, modify, and delete metadata headers in source files.

## Index

- [Usage](#usage)
- [Supported file types](#supported-file-types)
- [Installation](#installation)
- [Examples](#examples)
- [Tests](#tests)

## Usage

```
python main.py <flag> <file>
```

| Flag | Action |
|------|--------|
| `-v` | View metadata |
| `-m` | Modify metadata (updates the `Revised` timestamp) |
| `-c` | Create metadata header |
| `-d` | Delete metadata header |
| `-h` / `-?` / `?` / `--help` | Show help |

## Supported file types

| Extension | Comment style | Shebang |
|-----------|---------------|---------|
| `.py` | Module docstring (`"""..."""`) | `#!/usr/bin/env python3` |
| `.sh` | `#+` | `#! /bin/sh` |
| `.bash` | `#+` | `#! /bin/bash` |
| `.rs` | `//+` | — |
| `.md` | `[//]: # (+...)` | — |
| any other | `#+` (fallback) | — |

## Installation

Single-file script, no dependencies beyond the Python 3 standard library.

```sh
curl -O https://raw.githubusercontent.com/<user>/metadatos/main/main.py
python main.py -h
```

## Examples

### Python

```python
#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/17 10:00:00.000000
Revised: 2026/03/17 10:00:00.000000
"""
```

### Shell

```sh
#! /bin/sh
# ---------------------------------------------------------------------------
#+ Authors: 	Ran# <ran.hash@proton.me>
#+ Created: 	2026/03/17 10:00:00.000000
#+ Revised: 	2026/03/17 10:00:00.000000
# ---------------------------------------------------------------------------
```

### Rust

```rust
// ---------------------------------------------------------------------------
//+ Authors: 	Ran# <ran.hash@proton.me>
//+ Created: 	2026/03/17 10:00:00.000000
//+ Revised: 	2026/03/17 10:00:00.000000
// ---------------------------------------------------------------------------
```

### Markdown

```markdown
[//]: # ( --------------------------------------------------------------------------- )
[//]: # (+ Authors: 	Ran# <ran.hash@proton.me> )
[//]: # (+ Created: 	2026/03/17 10:00:00.000000 )
[//]: # (+ Revised: 	2026/03/17 10:00:00.000000 )
[//]: # ( --------------------------------------------------------------------------- )
```

See the [samples/](samples/) folder for complete sample files.

## Tests

Run with:

```sh
python -m pytest test_metadatos.py
```

Coverage (74 tests):

| Area | What is tested |
|------|----------------|
| `save_file` / `load_file` | string and list round-trip, directory auto-creation, missing file error, empty list, no BOM |
| `format_now` | with/without microseconds, custom separators |
| `read_input` | no args, all help flags (`-h`, `?`, `-?`, `--help`), unknown flag, missing file argument, all valid flags |
| `show` | `.py` prints only docstring lines; `.sh`, `.rs`, `.md` print only metadata lines; non-metadata lines never appear; empty files print nothing |
| `edit` | `.py`, `.sh`, `.rs`, `.md` — `Revised` changes, `Authors`/`Created` unchanged, code preserved, noop on files with no metadata, `end` closer preserved for `.md`, no trailing closer for `.rs` |
| `create` | `.py`, `.sh`, `.rs`, `.md`, fallback — exact header structure, shebang present/absent per type, `end` closer on `.md` lines, code preserved, body-shorter-than-header not lost, idempotent on all types |
| `remove` | `.py`, `.sh`, `.rs`, `.md` — metadata stripped, code/content kept, noop on empty files |
| `execute` | dispatches all four flags, `DEFAULT_FT` fallback for unknown extension |
| round-trips | full create→show→edit→remove cycle for `.py`, `.sh`, `.rs`, `.md` |
