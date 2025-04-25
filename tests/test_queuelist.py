from python_tca2.alignment_suggestion import AlignmentSuggestion
from python_tca2.queue_entry import QueueEntry
from python_tca2.tca2path import Tca2Path


def test_is_hit():
    path = Tca2Path(initial_position=[0, 0])
    path.alignment_suggestions.extend(
        [
            AlignmentSuggestion([1, 0]),
            AlignmentSuggestion([0, 1]),
            AlignmentSuggestion([0, 0]),
        ]
    )
    queue_entry = QueueEntry(
        path=path,
        score=0,
    )

    assert not queue_entry.has_hit([1, 1])
    assert queue_entry.has_hit([0, 0])
