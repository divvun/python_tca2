from python_tca2.pathstep import PathStep
from python_tca2.steplist import create_step_list, int_to_base


def test_int_to_base():
    assert int_to_base(number=10, base=2) == "1010"
    assert int_to_base(number=10, base=8) == "12"
    assert int_to_base(number=10, base=10) == "10"
    assert int_to_base(number=10, base=3) == "101"
    assert int_to_base(number=10, base=5) == "20"


def test_create_step_list():
    assert create_step_list(num_files=2) == [
        PathStep(increment=[0, 1]),
        PathStep(increment=[1, 0]),
        PathStep(increment=[1, 1]),
        PathStep(increment=[1, 2]),
        PathStep(increment=[2, 1]),
    ]
    assert create_step_list(num_files=3) == [
        PathStep(increment=[0, 0, 1]),
        PathStep(increment=[0, 1, 0]),
        PathStep(increment=[0, 1, 1]),
        PathStep(increment=[1, 0, 0]),
        PathStep(increment=[1, 0, 1]),
        PathStep(increment=[1, 1, 0]),
        PathStep(increment=[1, 1, 1]),
    ]
