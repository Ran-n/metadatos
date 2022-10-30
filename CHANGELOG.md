[//]: # ( -*- coding: utf-8 -*- )
[//]: # ( ------------------------------------------------------------------------ )
[//]: # (+ Autor:  	Ran# )
[//]: # (+ Creado: 	2022/10/30 10:45:16.800195 )
[//]: # (+ Editado:	2022/10/30 12:44:43.475094 )
[//]: # ( ------------------------------------------------------------------------ )

# Changelog

## 1.1

### Features

- Now supports comment indicators of all sizes.
- Now supports .md files out of the box.
- Now only creates a start line execute if the ! is present, formerly it was always created.

### Fixes

- Fixed bug where it would only allow comment indicators of a max size (removed the startswith end optional parameter).

### Full Changes

- Removed the end parameter on all three startswith funtions.
- Insert of first line with execution indication only if the ! given in the "x_tipo_fich" list.
- Removed the check for length of 1st line before inserting it or not, now just checks for the ! symbol.
- Created "CHANGELOG.md" file.
- Improved "README.md" file.
- Changed default command (for when doesnt know the extension) from #! to # so that, it doesnt create a first line with just #!
- When you did metadata -s and then metadata -c it created some repeated junk lines, this is now fixed.
