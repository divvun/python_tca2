from unittest.mock import MagicMock

import pytest

from python_tca2.aelement import AlignmentElement
from python_tca2.alignment_suggestion import AlignmentSuggestion
from python_tca2.elementinfotobecompared import ElementInfoToBeCompared


@pytest.fixture
def mock_nodes():
    anchor_word_list = MagicMock()
    anchor_word_list.get_anchor_word_hits.return_value = (
        []
    )  # Mock the method to return an empty list or appropriate value
    text = "mock_text"  # Replace with a mock or appropriate value
    return [
        [
            AlignmentElement(anchor_word_list, text, text_number=0, element_number=i)
            for i in range(5)
        ],
        [
            AlignmentElement(anchor_word_list, text, text_number=1, element_number=i)
            for i in range(5)
        ],
    ]


def test_build_elementstobecompared_success_first_element(mock_nodes):
    element_info = ElementInfoToBeCompared()
    position = (-1, -1)
    alignment_suggestion = AlignmentSuggestion((1, 2))

    element_info.build_elementstobecompared(position, alignment_suggestion, mock_nodes)
    assert len(element_info.info[0]) == alignment_suggestion[0]
    assert len(element_info.info[1]) == alignment_suggestion[1]

    assert [i.element_number for i in element_info.info[0]] == [0]
    assert [i.element_number for i in element_info.info[1]] == [0, 1]


def test_build_elementstobecompared_success(mock_nodes):
    element_info = ElementInfoToBeCompared()
    position = (2, 2)
    alignment_suggestion = AlignmentSuggestion((1, 2))

    element_info.build_elementstobecompared(position, alignment_suggestion, mock_nodes)
    assert len(element_info.info[0]) == alignment_suggestion[0]
    assert len(element_info.info[1]) == alignment_suggestion[1]

    assert [i.element_number for i in element_info.info[0]] == [3]
    assert [i.element_number for i in element_info.info[1]] == [3, 4]


def test_build_elementstobecompared_end_of_text_exception(mock_nodes):
    element_info = ElementInfoToBeCompared()
    position = (3, 3)
    alignment_suggestion = AlignmentSuggestion((1, 2))

    element_info.build_elementstobecompared(position, alignment_suggestion, mock_nodes)

    assert len(element_info.info[0]) == 1
    assert len(element_info.info[1]) == 1


def test_build_elementstobecompared_end_of_all_texts_exception(mock_nodes):
    element_info = ElementInfoToBeCompared()
    position = (4, 3)
    alignment_suggestion = AlignmentSuggestion((1, 2))

    element_info.build_elementstobecompared(position, alignment_suggestion, mock_nodes)

    assert len(element_info.info[0]) == 0
    assert len(element_info.info[1]) == 1
