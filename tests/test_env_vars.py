import os

from dotenv import load_dotenv

from lof.env_vars import path_for_env_file, set_env_variables

current_dir = os.path.dirname(os.path.abspath(__file__))
test_json_vars = os.path.join(current_dir, "test_data/vars.json")
test_env_vars = os.path.join(current_dir, "test_data/.env")
lof_dir = ".lof"


def test_path_for_env_file():
    expected = ".lof/.env"
    os.makedirs(lof_dir, exist_ok=True)
    assert path_for_env_file(test_json_vars, lof_dir) == expected
    # check no issues
    assert load_dotenv(expected) is True


def test_set_env_variables_json():
    # check no issues
    assert set_env_variables(test_json_vars) is None
    assert os.environ["DB_USER"] == "test"


def test_set_env_variables_env():
    # check no issues
    assert set_env_variables(test_env_vars) is None
    assert os.environ["TEST_ENV"] == "DB_NAME_TEST"
