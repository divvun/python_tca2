from python_tca2.aelement import AlignmentElement

AlignedSentenceElements = tuple[list[AlignmentElement], list[AlignmentElement]]
"""A representation of aligned sentences.

Each item of the tuple represents the parts of each document that are parallels of each 
other.
"""


def to_string_tuple(
    aligned_sentence_elements: AlignedSentenceElements,
) -> tuple[str, str]:
    """Convert an AlignedSentenceElements into a tuple of strings.

    Args:
        aligned_sentence_elements: The aligned sentence elements to convert.

    Returns:
        A tuple of strings, each representing a translation pair.
    """
    return (
        " ".join(
            [
                alignment_element.text
                for alignment_element in aligned_sentence_elements[0]
            ]
        ),
        " ".join(
            [
                alignment_element.text
                for alignment_element in aligned_sentence_elements[1]
            ]
        ),
    )
