from dataclasses import dataclass


@dataclass
class AElement:
    text: str
    element_number: int
    alignment_number: int = -1

    @property
    def length(self) -> int:
        return len(self.text)
