from dataclasses import dataclass

from python_tca2.aelement import AlignmentElement


@dataclass
class AlignedSentenceElements:
    """A representation of aligned sentences.

    Attributes:
        elements: each item of the tuple represents a part of each document
                  that are parallels of each other.
    """

    elements: tuple[list[AlignmentElement], ...]

    def to_tuple(self) -> tuple[str, ...]:
        """Convert the AlignmentElements into a tuple of strings.

        Iterates over the values of the `elements` attribute, joining the text
        of each sub-element with a space, and returns the result as a tuple.
        """
        return tuple(
            " ".join([aelement.text for aelement in aelements])
            for aelements in self.elements
        )
