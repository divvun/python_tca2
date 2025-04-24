from python_tca2.pathstep import PathStep
from python_tca2.steplist import create_step_list


def test_create_step_list():
    assert create_step_list(num_files=2) == [
        PathStep((0, 1)),
        PathStep((1, 0)),
        PathStep((1, 1)),
        PathStep((1, 2)),
        PathStep((2, 1)),
    ]
    assert create_step_list(num_files=3) == [
        PathStep((0, 0, 1)),
        PathStep((0, 1, 0)),
        PathStep((0, 1, 1)),
        PathStep((1, 0, 0)),
        PathStep((1, 0, 1)),
        PathStep((1, 1, 0)),
        PathStep((1, 1, 1)),
    ]
