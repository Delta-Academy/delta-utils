from pathlib import Path

DONT_SEARCH = [
    "venv",
    ".git",
    "__pycache__",
    "dist",
    "build",
    "tests",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
]


def find_file(filename: str) -> Path:
    """Find game_mechanics.py within all child directories of the directory this is run from."""
    # Gets directory we're running from
    path = Path("").resolve()

    # Checks current directory
    if (path / filename).exists():
        return path / filename

    # Checks all child directories
    for item in path.iterdir():
        # Skip files and directories we don't want to search
        if item.name in DONT_SEARCH or item.is_file():
            continue

        # Search all ancestors
        paths = list(filter(lambda x: x.name == filename, item.rglob("*")))
        if paths:
            return paths[0]
    raise FileNotFoundError(f"Could not find {filename}")
