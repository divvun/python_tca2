from dataclasses import dataclass

from python_tca2.queue_entry import QueueEntry


@dataclass
class QueueList:
    """QueueList is a container for managing a list of queue entries."""

    entries: list[QueueEntry]

    def empty(self) -> bool:
        return len(self.entries) == 0

    def add(self, queue_entry: QueueEntry) -> None:
        """Add a queue entry to the list of entries.

        Args:
            queue_entry: The queue entry to be added.
        """
        self.entries.append(queue_entry)

    def contains(self, queue_entry: QueueEntry) -> bool:
        return queue_entry in self.entries

    def remove(self, pos: list[int]) -> None:
        for queue_entry in self.entries:
            if queue_entry.has_hit(pos):
                queue_entry.remove()

    def remove_for_real(self) -> None:
        """Removes entries marked as removed from the queue.

        Iterates through the list of entries, identifies those marked as removed,
        and deletes them from the queue.
        """
        to_remove = [queue_entry for queue_entry in self.entries if queue_entry.removed]

        for queue_entry in to_remove:
            self.entries.remove(queue_entry)
