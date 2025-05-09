from python_tca2.alignment_suggestion import AlignmentSuggestion
from python_tca2.path_candidate import PathCandidate


def test_is_hit():
    path_candidate = PathCandidate(
        position=[1, 1],
        alignment_suggestions=[
            AlignmentSuggestion([1, 0]),
            AlignmentSuggestion([0, 1]),
        ],
    )

    assert path_candidate.has_hit([1, 1])
    assert not path_candidate.has_hit([1, 2])
