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


def get_current_dir():
    return Path("").resolve()


def find_file(filename: str) -> Path:
    """Find game_mechanics.py within all child directories of the directory this is run from."""
    # Gets directory we're running from
    path = get_current_dir()

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


def find_folder(folder_name: str) -> Path:

    path = get_current_dir()
    end_me = False
    for p in path.rglob("*"):

        for dont in DONT_SEARCH:
            if dont in str(p):
                end_me = True
                break

        if end_me:
            end_me = False
            continue

        if p.name == folder_name and p.is_dir() and p not in DONT_SEARCH:
            return p

    raise FileNotFoundError(f"Could not find folder {folder_name}")
