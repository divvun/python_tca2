from dataclasses import dataclass


@dataclass
class AElement:
    text: str
    element_number: int

    @property
    def length(self) -> int:
        return len(self.text)
