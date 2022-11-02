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
    """Find game_mechanics.py."""
    path = Path("").resolve()

    if (path / filename).exists():
        return path / filename

    for item in path.iterdir():
        if item.name in DONT_SEARCH or item.is_file():
            continue

        if paths := list(filter(lambda x: x.name == filename, item.rglob("*"))):
            return paths[0]
    raise FileNotFoundError(f"Could not find {filename}")
