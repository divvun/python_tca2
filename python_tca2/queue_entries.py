from dataclasses import dataclass

from python_tca2.queue_entry import QueueEntry


@dataclass
class QueueEntries:
    """QueueEntries is a container for managing a list of queue entries."""

    entries: list[QueueEntry]
