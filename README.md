# File Organizer

## Purpose

`file_organizer.py` is a small command-line utility for sorting files into class folders based on filename patterns.

It is designed for files named like:

- `csc3380lec1.pptx`
- `math101lec12.pdf`
- `csc3380hw3.docx`
- `bio220_lab2.csv`

For each matching file, it:

1. Detects the course code prefix (for example, `csc3380`)
2. Detects an optional numbered activity token such as `lec`, `lecture`, `hw`, `homework`, `lab`, `quiz`, `exam`, or `project`
3. Creates a course folder in the target directory (for example, `CSC3380`)
4. Accepts synonyms and normalizes token folders to abbreviations (for example, `lecture` -> `LEC`, `homework` -> `HW`)
5. If a numbered activity token is present, creates a token subfolder (for example, `CSC3380/HW`)
6. Moves the file into the matching folder
7. If a numbered activity token is present, renames the file with a zero-padded numeric prefix and abbreviation token for sorting (for example, `001_csc3380lec1.pptx`, `003_csc3380hw3.docx`)

## Design

The script follows a simple single-pass design:

- It scans top-level files by default and optionally scans nested folders with `--recursive`.
- It uses two regex patterns:
	- `^([a-z]{2,}\d+[a-z]?)\W*(?:lec|lecture|hw|homework|lab|quiz|exam|project)\W*(\d+)` for class + numbered activity files
	- `^([a-z]{2,}\d+[a-z]?)` for other similarly named class files
- It normalizes course folder names to uppercase.
- It places numbered activity files in abbreviation subfolders (for example, `LEC`, `HW`, `LAB`, `PROJ`).
- It accepts synonym inputs and maps them to one canonical abbreviation (for example, `lecture` and `lec` both map to `LEC`).
- It skips files without a class prefix.
- It avoids overwriting by adding `_1`, `_2`, and so on when a destination filename already exists.

This design keeps behavior predictable and easy to review in batch operations.

## Safety Mode

Use `--dry-run` to preview all folder creation and move/rename actions without changing files.

## Usage

Run from this project folder or any location that can access the script:

```powershell
py file_organizer.py "C:\path\to\target-folder" --dry-run
py file_organizer.py "C:\path\to\target-folder"
py file_organizer.py "C:\path\to\target-folder" --recursive
```

## Example

Input files in one folder:

- `csc3380lecture1.pptx`
- `csc3380lec2.pdf`
- `csc3380homework3.docx`
- `math101lec1.docx`
- `math101_notes.txt`

Result:

- `CSC3380/LEC/001_csc3380lec1.pptx`
- `CSC3380/LEC/002_csc3380lec2.pdf`
- `CSC3380/HW/003_csc3380hw3.docx`
- `MATH101/LEC/001_math101lec1.docx`
- `MATH101/math101_notes.txt`

## Current Limits

- Class detection depends on a class-prefix pattern such as `csc3380` or `math101` at the start of the filename.
- Files without a recognized class prefix are skipped.
