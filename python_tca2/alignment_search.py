from typing import Iterator

from python_tca2 import alignment_suggestion, constants
from python_tca2.aligned_sentence_elements import AlignedSentenceElements
from python_tca2.alignment_suggestion import AlignmentSuggestion
from python_tca2.candidate_alignment import CandidateAlignment
from python_tca2.path_candidate import PathCandidate
from python_tca2.rolling_document import RollingDocument


class _BeamRound:
    """Collects the candidates produced while extending one beam-search step."""

    def __init__(self, current: list[PathCandidate]) -> None:
        self._current = current
        self.next: list[PathCandidate] = []

    def add(self, candidate: PathCandidate) -> None:
        if not candidate.end:
            self._mark_hits_as_removed(candidate.position)
            self.next.append(candidate)
        elif candidate not in self.next:
            self.next.append(candidate)

    def _mark_hits_as_removed(self, position: tuple[int, int]) -> None:
        for candidate_list in (self._current, self.next):
            for candidate in candidate_list:
                if candidate.has_hit(position):
                    candidate.removed = True


class AlignmentSearch:
    """Search alignments over a bounded pair of rolling documents."""

    def __init__(
        self,
        documents: tuple[RollingDocument, RollingDocument],
    ) -> None:
        self._documents = documents
        self._step_scores: dict[tuple[slice, slice], float] = {}
        self._max_path_length = constants.MAX_PATH_LENGTH

    @property
    def max_buffer_size(self) -> int:
        return sum(document.max_buffer_size for document in self._documents)

    def get_aligned_sentence_elements(
        self, slices: tuple[slice, slice]
    ) -> AlignedSentenceElements:
        return (
            self._documents[0].get_slice(slices[0]),
            self._documents[1].get_slice(slices[1]),
        )

    def will_reach_both_ends(self, position: tuple[int, int]) -> bool:
        return all(
            document.is_past_end(current_position)
            for current_position, document in zip(
                position,
                self._documents,
                strict=True,
            )
        )

    def will_reach_one_end(self, position: tuple[int, int]) -> bool:
        return any(
            document.is_past_end(current_position)
            for current_position, document in zip(
                position,
                self._documents,
                strict=True,
            )
        )

    def retrieve_alignment_suggestion(
        self,
        start_position: tuple[int, int],
    ) -> AlignmentSuggestion | None:

        path_candidates = self.extend_alignment_paths(start_position=start_position)

        if (
            len(path_candidates) < constants.NUM_FILES
            and not path_candidates[0].alignment_suggestions
        ):
            # When the length of the queue list is less than the number of files
            # and the first path in the queue list has no steps, then aligment
            # is done
            return None

        return self.select_best_alignment_suggestion(path_candidates)

    def select_best_alignment_suggestion(
        self, path_candidates: list[PathCandidate]
    ) -> AlignmentSuggestion | None:
        """Select the first step of the path with the highest normalized score."""
        score_step_list = [
            (
                candidate_entry.normalized_score,
                candidate_entry.alignment_suggestions[0],
            )
            for candidate_entry in path_candidates
        ]

        return max(score_step_list, key=lambda x: x[0])[1] if score_step_list else None

    def extend_alignment_paths(
        self,
        start_position: tuple[int, int],
    ) -> list[PathCandidate]:
        """Extend paths until no further extensions are possible or the max length is reached."""
        best_path_scores: dict[tuple[int, ...], float] = {}
        path_candidates = [PathCandidate(position=start_position)]
        for _ in range(self._max_path_length):
            beam_round = _BeamRound(path_candidates)
            for path_candidate in path_candidates:
                if not path_candidate.removed and not path_candidate.end:
                    for new_candidate in self.extend_current_path(
                        path_candidate,
                        best_path_scores=best_path_scores,
                    ):
                        beam_round.add(new_candidate)

            if not beam_round.next:
                return path_candidates

            path_candidates = [c for c in beam_round.next if not c.removed]

        return path_candidates

    def extend_current_path(
        self,
        path_candidate: PathCandidate,
        best_path_scores: dict[tuple[int, ...], float],
    ) -> Iterator[PathCandidate]:
        """Yield each way the current path can be extended by one alignment step."""
        for step in alignment_suggestion.generate_alignment_suggestions(
            len(self._documents)
        ):
            candidate = self.extend_path_with_step(
                old_position=path_candidate.position,
                old_score=path_candidate.score,
                alignment_suggestions=path_candidate.alignment_suggestions + [step],
                best_path_scores=best_path_scores,
            )
            if candidate is not None:
                yield candidate

    def get_step_score(
        self,
        slices: tuple[slice, slice],
    ) -> float:
        """Calculate (and cache) the score for the elements at the given slices."""
        if slices not in self._step_scores:
            eitbc = CandidateAlignment(
                aligned_sentence_elements=self.get_aligned_sentence_elements(
                    slices=slices,
                )
            )
            self._step_scores[slices] = eitbc.get_score()

        return self._step_scores[slices]

    def extend_path_with_step(
        self,
        old_position: tuple[int, int],
        old_score: float,
        alignment_suggestions: list[AlignmentSuggestion],
        best_path_scores: dict[tuple[int, ...], float],
    ) -> PathCandidate | None:
        """Extend a path with a new step, returning the extended candidate if it improves on the best known score for its position."""
        current_alignment_step = alignment_suggestions[-1]
        new_position = (
            old_position[0] + current_alignment_step[0],
            old_position[1] + current_alignment_step[1],
        )

        if self.will_reach_both_ends(new_position):
            return PathCandidate(
                position=old_position,
                score=old_score,
                alignment_suggestions=alignment_suggestions[:-1],
                end=True,
            )

        if self.will_reach_one_end(new_position):
            return None

        position_step_score = self.get_step_score(
            slices=(
                slice(old_position[0], new_position[0]),
                slice(old_position[1], new_position[1]),
            )
        )

        if position_step_score == constants.ELEMENTINFO_SCORE_HOPELESS:
            return None

        new_score = old_score + position_step_score

        best_path_score = get_best_path_score(
            new_position, best_path_scores=best_path_scores
        )

        if best_path_score is not None and new_score <= best_path_score:
            return None

        set_best_path_score(
            new_position,
            new_score,
            best_path_scores=best_path_scores,
        )

        return PathCandidate(
            position=new_position,
            score=new_score,
            alignment_suggestions=alignment_suggestions,
        )

    def iter_alignment_elements(self) -> Iterator[AlignedSentenceElements]:
        """Yield committed alignments while retaining only the search horizon."""
        start_position = (0, 0)
        while (
            suggestion := self.retrieve_alignment_suggestion(
                start_position=start_position
            )
        ) is not None:
            next_position = (
                start_position[0] + suggestion[0],
                start_position[1] + suggestion[1],
            )
            yield self.get_aligned_sentence_elements(
                slices=(
                    slice(start_position[0], next_position[0]),
                    slice(start_position[1], next_position[1]),
                )
            )
            for document, position in zip(
                self._documents, next_position, strict=True
            ):
                document.discard_before(position)
            self._step_scores.clear()
            start_position = next_position


def set_best_path_score(
    position: tuple[int, ...],
    score: float,
    best_path_scores: dict[tuple[int, ...], float],
) -> None:
    """Record the score for a path reaching the given position."""
    best_path_scores[position] = score


def get_best_path_score(
    position: tuple[int, ...], best_path_scores: dict[tuple[int, ...], float]
) -> float | None:
    """Return the best known score for the given position, or None if unseen."""
    if any(pos == 0 for pos in position):
        return constants.BEST_PATH_SCORE_BAD

    return best_path_scores.get(position)
