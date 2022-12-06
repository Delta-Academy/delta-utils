import datetime
import warnings
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple, Type, Union

from delta_utils.hash_game_mechanics import hash_game_mechanics, load_game_mechanics_hash


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


def check_submission(
    example_state: Any,
    expected_choose_move_return_type: Type,
    current_folder: Path,
    pkl_file: Optional[Any] = None,
    expected_pkl_type: Union[None, Type, Tuple[Type, ...]] = None,
    pkl_checker_function: Optional[Callable] = None,
    choose_move_extra_argument: Optional[Dict[str, Any]] = None,
    game_mechanics_hash: Optional[str] = None,
) -> None:
    """Checks a user submission is valid.

    Args:
        example_state (any): Example of the argument to the user's choose_move function
        expected_choose_move_return_type (Type): of the users choose_move_function
        current_folder (Path): The folder path of the user's game code (main.py etc)
        pkl_file (any): The user's loaded pkl file (None if not using a stored pkl file)
        expected_pkl_type (Type): Expected type of the above (None if not using a stored pkl file)
        pkl_checker_function (callable): The function to check that pkl_file is valid
                                         (None if not using a stored pkl file)
        game_mechanics_hash (str): DEPRECATED sha256 hash of game_mechanics.py (see
                                    hash_game_mechanics())
    """
    if game_mechanics_hash is not None:
        warnings.warn(
            "game_mechanics_hash is deprecated, please remove this argument from check_submission()",
            DeprecationWarning,
        )

    if (current_folder / "game_mechanics_hash.txt").exists():
        game_mechanics_path = current_folder
    elif (current_folder / "game_mechanics" / "game_mechanics_hash.txt").exists():
        game_mechanics_path = current_folder / "game_mechanics"
    else:
        raise FileNotFoundError(
            f"game_mechanics_hash.txt not found in {current_folder} or {current_folder / 'game_mechanics'}"
        )

    assert hash_game_mechanics(game_mechanics_path) == load_game_mechanics_hash(
        game_mechanics_path
    ), (
        "You've changed game_mechanics.py, please don't do this! :'( "
        "(if you can't escape this error message, reach out to us on slack)"
    )

    main = current_folder / "main.py"
    assert main.exists(), "You need a main.py file!"
    assert main.is_file(), "main.py isn't a Python file!"

    file_name = main.stem

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
        raise AttributeError(f"No function 'choose_move()' found in file {file_name}.py") from e

    if choose_move_extra_argument is not None:

        # Dear god this needs refactoring
        if pkl_file is not None:

            def choose_move_wrap(example_state, pkl_file):
                """only works with neural network currently."""
                return choose_move(
                    example_state,
                    neural_network=pkl_file,
                    **choose_move_extra_argument,
                )

        else:

            def choose_move_wrap(example_state):
                """only works with neural network currently."""
                return choose_move(
                    example_state,
                    **choose_move_extra_argument,
                )

    else:
        choose_move_wrap = choose_move

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

    if pkl_file is not None:
        assert expected_pkl_type is not None and pkl_checker_function is not None, (
            "You must pass an arugment for expected_pkl_type "
            "and pkl_checker_function if you pass a pkl_file"
        )
        try:
            assert isinstance(
                pkl_file, expected_pkl_type
            ), f"The .pkl file you saved is the wrong type! It should be a {expected_pkl_type}"
            pkl_checker_function(pkl_file)
            action = choose_move_wrap(example_state, pkl_file)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Value dictionary file called 'dict_{team_name}.pkl' cannot be found! "
                f"Check the file exists & that the name matches."
            ) from e
    else:
        # Wrapper for extra argument not implemented
        action = choose_move_wrap(example_state)

    assert isinstance(action, expected_choose_move_return_type), (
        f"Action output by `choose_move()` must be type {expected_choose_move_return_type}, "
        f"but instead {action} of type {type(action)} was output."
    )
    congrats_str = "Congratulations! Your Repl is ready to submit :)"
    if pkl_file is not None:
        congrats_str += f"It'll be using value function file called 'dict_{team_name}.pkl'"
    print(congrats_str)


def pkl_checker_value_dict(pkl_file: Dict) -> None:
    """Checks a dictionary acting as a value lookup table."""
    if isinstance(pkl_file, defaultdict):
        assert not callable(
            pkl_file.default_factory
        ), "Please don't use functions within default dictionaries in your pickle file!"

    assert len(pkl_file) > 0, "Your dictionary is empty!"

    for k, v in pkl_file.items():
        assert isinstance(
            v, (float, int)
        ), f"Your value function dictionary values should all be numbers, but for key {k}, the value {v} is of type {type(v)}!"
