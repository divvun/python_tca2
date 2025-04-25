from python_tca2.alignment_suggestion import (
    AlignmentSuggestion,
    generate_alignment_suggestions,
)


def test_create_step_list():
    assert generate_alignment_suggestions(num_files=2) == [
        AlignmentSuggestion((0, 1)),
        AlignmentSuggestion((1, 0)),
        AlignmentSuggestion((1, 1)),
        AlignmentSuggestion((1, 2)),
        AlignmentSuggestion((2, 1)),
    ]
    assert generate_alignment_suggestions(num_files=3) == [
        AlignmentSuggestion((0, 0, 1)),
        AlignmentSuggestion((0, 1, 0)),
        AlignmentSuggestion((0, 1, 1)),
        AlignmentSuggestion((1, 0, 0)),
        AlignmentSuggestion((1, 0, 1)),
        AlignmentSuggestion((1, 1, 0)),
        AlignmentSuggestion((1, 1, 1)),
    ]
