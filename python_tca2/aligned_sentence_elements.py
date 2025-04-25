from python_tca2.aelement import AlignmentElement

AlignedSentenceElements = tuple[list[AlignmentElement], ...]
"""A representation of aligned sentences.

Each item of the tuple represents the parts of each document that are parallels of each 
other.
"""


def to_string_tuple(
    aligned_sentence_elements: AlignedSentenceElements,
) -> tuple[str, ...]:
    """Convert the AlignmentElements into a tuple of strings.

    Iterates over the values of the `elements` attribute, joining the text
    of each sub-element with a space, and returns the result as a tuple.
    """
    return tuple(
        " ".join([aelement.text for aelement in aelements])
        for aelements in aligned_sentence_elements
    )
