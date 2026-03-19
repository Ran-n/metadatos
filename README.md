[//]: # ( --------------------------------------------------------------------------- )
[//]: # (+  Authors: 	Ran# <ran.hash@proton.me> )
[//]: # (+  Created: 	2022/10/30 10:37:41.000000 )
[//]: # (+  Revised: 	2026/03/17 10:00:00.000000 )
[//]: # ( --------------------------------------------------------------------------- )

# metadatos

A CLI tool to create, view, modify, and delete metadata headers in source files.

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
| `-h` / `?` | Show help |

## Supported file types

| Extension | Format |
|-----------|--------|
| `.py` | Module docstring (`"""..."""`) |
| `.sh` / `.bash` | `#+` comments |
| `.rs` | `//+` comments |
| `.md` | `[//]: # (+...)` comments |
| any other | `#+` comments (fallback) |

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
[//]: # (+  Authors: 	Ran# <ran.hash@proton.me> )
[//]: # (+  Created: 	2026/03/17 10:00:00.000000 )
[//]: # (+  Revised: 	2026/03/17 10:00:00.000000 )
[//]: # ( --------------------------------------------------------------------------- )
```

See the [samples/](samples/) folder for complete sample files.

## Installation

Single-file script, no dependencies beyond the Python 3 standard library.

```sh
curl -O https://raw.githubusercontent.com/<user>/metadatos/main/main.py
python main.py -h
```
