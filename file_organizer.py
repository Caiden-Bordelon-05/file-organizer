#!/usr/bin/env python3
import argparse
import re
import shutil
from pathlib import Path

TOKEN_ALIASES = {
    "lec": "LEC",
    "lecture": "LEC",
    "hw": "HW",
    "homework": "HW",
    "lab": "LAB",
    "quiz": "QUIZ",
    "exam": "EXAM",
    "project": "PROJ",
}

# Examples matched: csc3380lec1, CSC3380_lecture12, math101-hw-03, bio220_lab2
NUMBERED_TAG_PATTERN = re.compile(
    r"^([a-z]{2,}\d+[a-z]?)\W*(lec|lecture|hw|homework|lab|quiz|exam|project)\W*(\d+)",
    re.IGNORECASE,
)
# Examples matched: csc3380_notes, MATH101_hw2, bio220-lab1
COURSE_PREFIX_PATTERN = re.compile(r"^([a-z]{2,}\d+[a-z]?)", re.IGNORECASE)


def unique_destination(path: Path) -> Path:
    """Return a unique destination path if the original target already exists."""
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 1
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def course_from_name(stem: str) -> tuple[str | None, str | None, int | None]:
    tag_match = NUMBERED_TAG_PATTERN.match(stem)
    if tag_match:
        token = tag_match.group(2).lower()
        token_abbreviation = TOKEN_ALIASES.get(token, token.upper())
        return tag_match.group(1).upper(), token_abbreviation, int(tag_match.group(3))

    course_match = COURSE_PREFIX_PATTERN.match(stem)
    if course_match:
        return course_match.group(1).upper(), None, None

    return None, None, None


def organize_files(directory: str, dry_run: bool = False, recursive: bool = False) -> None:
    base_dir = Path(directory)
    if not base_dir.exists() or not base_dir.is_dir():
        print(f"Directory does not exist: {base_dir}")
        return

    files = base_dir.rglob("*") if recursive else base_dir.iterdir()

    for source in files:
        if not source.is_file():
            continue
        if source.parent != base_dir and not recursive:
            continue

        course, activity_token, sequence_number = course_from_name(source.stem)
        if not course:
            print(f"Skipped {source.name}: no class prefix found")
            continue

        class_dir = base_dir / course
        if not class_dir.exists():
            if dry_run:
                print(f"Would create directory: {class_dir}")
            else:
                class_dir.mkdir(parents=True, exist_ok=True)
                print(f"Created directory: {class_dir}")

        if activity_token:
            target_dir = class_dir / activity_token
            if not target_dir.exists():
                if dry_run:
                    print(f"Would create directory: {target_dir}")
                else:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    print(f"Created directory: {target_dir}")
        else:
            target_dir = class_dir

        if sequence_number is not None and activity_token is not None:
            normalized_stem = re.sub(
                r"(?i)\b(lec|lecture|hw|homework|lab|quiz|exam|project)\b",
                activity_token.lower(),
                source.stem,
                count=1,
            )
            target_name = f"{sequence_number:03d}_{normalized_stem}{source.suffix}"
        else:
            target_name = source.name

        destination = unique_destination(target_dir / target_name)
        if destination.resolve() == source.resolve():
            continue

        if dry_run:
            print(f"Would move {source} -> {destination}")
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            print(f"Moved {source.name} -> {destination.name} in {course}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Organize files into class folders based on class prefix in filenames."
    )
    parser.add_argument("directory", help="Directory to organize")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without moving files",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Scan subfolders in addition to the top-level directory",
    )
    args = parser.parse_args()
    organize_files(args.directory, dry_run=args.dry_run, recursive=args.recursive)