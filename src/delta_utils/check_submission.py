import datetime
import hashlib
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Set, Type

HERE = Path(__file__).parent.resolve()

"""
Example usage (connect4)

def pkl_checker(pkl_file: Dict) -> None:
    for v in pkl_file.values():
        assert isinstance(v, float), "Your value function dictionary values should be a float!"


def check_submission() -> None:

    example_state = get_empty_board()
    expected_choose_move_return_type = int
    pickle_loader = load_dictionary
    game_mechanics_hash = "1a5e3ad8dbd93fd9f3bd2212e1641ac969b827fce9ac185f7a9f0d13eeae6a1a"
    expected_pkl_output_type = dict
    pkl_checker_function = pkl_checker


"""


def hash_game_mechanics(path: Path) -> str:
    """Call me to generate game_mechanics_hash."""
    return sha256_file(path / "game_mechanics.py")


def get_local_imports(folder_path) -> Set:
    """Get the names of all files imported from folder_path."""
    local_imports = set()
    for module in sys.modules.values():
        if not hasattr(module, "__file__") or module.__file__ is None:
            continue
        path = Path(module.__file__)
        # Module is in this folder
        if Path(os.path.commonprefix([folder_path, path])) == folder_path:
            local_imports.add(path.stem)
    return local_imports


def check_submission(
    example_state: Any,
    expected_choose_move_return_type: Type,
    game_mechanics_hash: str,
    current_folder: Path,
    pkl_file: Optional[Any] = None,
    expected_pkl_type: Optional[Type] = None,
    pkl_checker_function: Optional[Callable] = None,
) -> None:
    """Checks a user submission is valid.

    Args:
        example_state (any): Example of the argument to the user's choose_move function
        expected_choose_move_return_type (Type): of the users choose_move_function
        game_mechanics_hash (str): sha256 hash of game_mechanics.py (see hash_game_mechanics())
        current_folder (Path): The folder path of the user's game code (main.py etc)
        pkl_file (any): The user's loaded pkl file (None if not using a stored pkl file)
        expected_pkl_type (Type): Expected type of the above (None if not using a stored pkl file)
        pkl_checker_function (callable): The function to check that pkl_file is valid
                                         (None if not using a stored pkl file)
    """
    assert hash_game_mechanics(current_folder) == game_mechanics_hash, (
        "You've changed game_mechanics.py, please don't do this! :'( "
        "(if you can't escape this error message, reach out to us on slack)"
    )

    local_imports = get_local_imports(current_folder)
    valid_local_imports = {"__main__", "__init__", "game_mechanics", "check_submission"}
    assert local_imports.issubset(valid_local_imports), (
        f"You imported {local_imports - valid_local_imports}. "
        f"Please do not import local files other than "
        f"check_submission and game_mechanics into your main.py."
    )

    mains = [entry for entry in os.scandir(current_folder) if entry.name == "main.py"]
    assert len(mains) == 1, "You need a main.py file!"
    main = mains[0]
    assert main.is_file(), "main.py isn't a Python file!"

    file_name = main.name.split(".py")[0]

    pre_import_time = datetime.datetime.now()
    mod = __import__(f"{file_name}", fromlist=["None"])
    time_to_import = (datetime.datetime.now() - pre_import_time).total_seconds()

    # Check importing takes a reasonable amount of time
    assert time_to_import < 2, (
        f"Your main.py file took {time_to_import} seconds to import.\n"
        f"This is much longer than expected.\n"
        f"Please make sure it's not running anything (training, testing etc) outside the "
        f"if __name__ == '__main__': at the bottom of the file"
    )

    # Check the choose_move() function exists
    try:
        choose_move = getattr(mod, "choose_move")
    except AttributeError as e:
        raise Exception(
            f"No function 'choose_move()' found in file {file_name}.py"
        ) from e

    # Check there is a TEAM_NAME attribute
    try:
        team_name = getattr(mod, "TEAM_NAME")
    except AttributeError as e:
        raise Exception(f"No TEAM_NAME found in file {file_name}.py") from e

    # Check TEAM_NAME isn't empty
    if len(team_name) == 0:
        raise ValueError(f"TEAM_NAME is empty in file {file_name}.py")

    # Check TEAM_NAME isn't still 'Team Name'
    if team_name == "Team Name":
        raise ValueError(
            f"TEAM_NAME='Team Name' which is what it starts as - "
            f"please change this in file {file_name}.py to your team name!"
        )

    if (
        pkl_file is not None
        and expected_pkl_type is not None
        and pkl_checker_function is not None
    ):  # lol mypy
        try:
            assert isinstance(
                pkl_file, expected_pkl_type
            ), f"The .pkl file you saved is the wrong type! It should be a {expected_pkl_type}"
            pkl_checker_function(pkl_file)
            action = choose_move(example_state, pkl_file)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Value dictionary file called 'dict_{team_name}.pkl' cannot be found! "
                f"Check the file exists & that the name matches."
            ) from e
    else:
        action = choose_move(example_state)

    assert isinstance(action, expected_choose_move_return_type), (
        f"Action output by `choose_move()` must be type {expected_choose_move_return_type}, "
        f"but instead {action} of type {type(action)} was output."
    )
    print(
        "Congratulations! Your Repl is ready to submit :)\n\n"
        f"It'll be using value function file called 'dict_{team_name}.pkl'"
    )


def sha256_file(filename: Path) -> str:
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, "rb", buffering=0) as f:
        while n := f.readinto(mv):  # type: ignore
            h.update(mv[:n])
    return h.hexdigest()


def pkl_checker_value_dict(pkl_file: Dict) -> None:
    """Checks a dictionary acting as a value lookup table."""
    if isinstance(pkl_file, defaultdict):
        assert not callable(
            pkl_file.default_factory
        ), "Please don't use functions within default dictionaries in your pickle file!"

    assert len(pkl_file) > 0, "Your dictionary is empty!"

    for v in pkl_file.values():
        assert isinstance(
            v, float
        ), "Your value function dictionary values should be a float!"
