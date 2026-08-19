from typing import Iterable, Iterator

from python_tca2.aligned_sentence_elements import AlignedSentenceElements
from python_tca2.alignment_search import AlignmentSearch
from python_tca2.anchorwordlist import AnchorWordList
from python_tca2.rolling_document import RollingDocument


class AlignmentModel:
    """An alignment model backed by bounded rolling input windows."""

    def __init__(
        self,
        sentences_tuple: tuple[Iterable[str], Iterable[str]],
        anchor_word_list: AnchorWordList,
    ) -> None:
        documents: tuple[RollingDocument, RollingDocument] = (
            RollingDocument(
                sentences=sentences_tuple[0],
                anchor_word_list=anchor_word_list,
                text_number=0,
            ),
            RollingDocument(
                sentences=sentences_tuple[1],
                anchor_word_list=anchor_word_list,
                text_number=1,
            ),
        )
        self.search = AlignmentSearch(documents)

    @property
    def max_buffer_size(self) -> int:
        return self.search.max_buffer_size

    def get_aligned_sentence_elements(
        self, slices: tuple[slice, slice]
    ) -> AlignedSentenceElements:
        """Return elements in the current search window for the supplied slices."""
        return self.search.get_aligned_sentence_elements(slices)

    def iter_alignment_elements(self) -> Iterator[AlignedSentenceElements]:
        return self.search.iter_alignment_elements()
