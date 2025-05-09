from dataclasses import dataclass

from python_tca2.path_candidate import PathCandidate


@dataclass
class PathCandidates:
    """QueueEntries is a container for managing a list of queue entries."""

    entries: list[PathCandidate]
