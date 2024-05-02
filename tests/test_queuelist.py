from python_tca2.path import Path
from python_tca2.pathstep import PathStep
from python_tca2.queue_entry import QueueEntry


def test_is_hit():
    path = Path(initial_position=[0, 0])
    path.steps.extend(
        [
            PathStep(increment=[1, 0]),
            PathStep(increment=[0, 1]),
            PathStep(increment=[0, 0]),
        ]
    )
    queue_entry = QueueEntry(
        path=path,
        score=0,
    )

    assert not queue_entry.has_hit([1, 1])
    assert queue_entry.has_hit([0, 0])
