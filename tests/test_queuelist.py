from python_tca2.alignment_suggestion import AlignmentSuggestion
from python_tca2.queue_entry import QueueEntry


def test_is_hit():
    queue_entry = QueueEntry(
        position=[1, 1],
        alignment_suggestions=[
            AlignmentSuggestion([1, 0]),
            AlignmentSuggestion([0, 1]),
        ],
    )

    assert queue_entry.has_hit([1, 1])
    assert not queue_entry.has_hit([1, 2])
