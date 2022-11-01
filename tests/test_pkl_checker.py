import pickle
from collections import defaultdict
from pathlib import Path

import pytest
from src.delta_utils.check_submission import pkl_checker_value_dict

HERE = Path(__file__).parent.resolve()


def test_pkl_checker_works() -> None:
    valid_dict = {"test": 1.0, "Test2": 2.0}
    valid_pkl_location = HERE / "valid_dict_test.pkl"
    with open(valid_pkl_location, "wb") as f:
        pickle.dump(valid_dict, f)

    with open(valid_pkl_location, "rb") as f:
        pkl_checker_value_dict(pickle.load(f))
    valid_pkl_location.unlink()


def def_value() -> float:
    return 0.0


def test_pkl_checker_should_fail() -> None:
    """Case directly from user code."""

    invalid_dict = defaultdict(def_value)
    invalid_dict["test"] = 1.0
    invalid_pkl_location = HERE / "invalid_dict_test.pkl"

    with open(invalid_pkl_location, "wb") as f:
        pickle.dump(invalid_dict, f)

    with open(invalid_pkl_location, "rb") as f:
        invalid = pickle.load(f)

    invalid_pkl_location.unlink()

    with pytest.raises(AssertionError):
        pkl_checker_value_dict(invalid)
