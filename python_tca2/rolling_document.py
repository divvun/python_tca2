from collections import deque
from typing import Iterable

from python_tca2.aelement import AlignmentElement
from python_tca2.anchorwordlist import AnchorWordList


class RollingDocument:
    """Lazily materialize alignment elements and discard committed input."""

    def __init__(
        self,
        sentences: Iterable[str],
        anchor_word_list: AnchorWordList,
        text_number: int,
    ) -> None:
        self._sentences = iter(sentences)
        self._anchor_word_list = anchor_word_list
        self._text_number = text_number
        self._elements: deque[AlignmentElement] = deque()
        self._buffer_start = 0
        self._next_element_number = 0
        self._exhausted = False
        self.max_buffer_size = 0

    def has_element(self, element_number: int) -> bool:
        if element_number < self._buffer_start:
            raise ValueError("Cannot read an element that has been discarded")

        while not self._exhausted and self._next_element_number <= element_number:
            try:
                sentence = next(self._sentences)
            except StopIteration:
                self._exhausted = True
                break

            self._elements.append(
                AlignmentElement(
                    anchor_word_list=self._anchor_word_list,
                    text=sentence,
                    text_number=self._text_number,
                    element_number=self._next_element_number,
                )
            )
            self._next_element_number += 1
            self.max_buffer_size = max(self.max_buffer_size, len(self._elements))

        return element_number < self._next_element_number

    def get_slice(self, element_slice: slice) -> list[AlignmentElement]:
        if element_slice.step not in (None, 1):
            raise ValueError("Only contiguous sentence slices are supported")
        if element_slice.start is None or element_slice.stop is None:
            raise ValueError("Sentence slices must have explicit bounds")
        if element_slice.start < self._buffer_start:
            raise ValueError("Cannot read an element that has been discarded")
        if element_slice.stop > element_slice.start:
            self.has_element(element_slice.stop - 1)

        end = min(element_slice.stop, self._next_element_number)
        return [
            self._elements[index - self._buffer_start]
            for index in range(element_slice.start, end)
        ]

    def is_past_end(self, position: int) -> bool:
        """Return whether an input position is beyond the document end."""
        if position <= self._buffer_start:
            return False
        return position > 0 and not self.has_element(position - 1)

    def discard_before(self, position: int) -> None:
        while self._buffer_start < position:
            self._elements.popleft()
            self._buffer_start += 1
