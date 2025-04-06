import json
from typing import List

from python_tca2.aelement import AElement
from python_tca2.anchorwordlist import AnchorWordList
from python_tca2.elementinfo import ElementInfo
from python_tca2.exceptions import EndOfTextExceptionError


class ElementsInfo:
    def __init__(self) -> None:
        self.first: int = 0
        self.last: int = -1
        self.element_info: List[ElementInfo] = []

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def to_json(self):
        return {
            "first": self.first,
            "last": self.last,
            "element_info": [
                element_info.to_json() for element_info in self.element_info
            ],
        }

    def get_element_info(
        self,
        nodes: dict[int, list[AElement]],
        anchor_word_list: AnchorWordList,
        element_number: int,
        text_number: int,
    ) -> ElementInfo:
        """Retrieve information about a specific element.

        Args:
            nodes: A dictionary mapping integers to lists of elements.
            anchor_word_list: A list of anchor words for processing.
            element_number: The number of the element to retrieve.
            text_number: The number of the text associated with the element.

        Returns:
            Information about the specified element.
        """
        if element_number < self.first:
            self.set_first(nodes, anchor_word_list, element_number, text_number)
        elif element_number > self.last:
            self.set_last(nodes, anchor_word_list, element_number, text_number)

        return self.element_info[element_number - self.first]

    def set_first(
        self,
        nodes: dict[int, list[AElement]],
        anchor_word_list: AnchorWordList,
        new_first: int,
        text_number: int,
    ) -> None:
        """Adjusts the range of elements in `element_info` based on `new_first`.

        This method updates the `element_info` list and the `first` attribute
        to reflect the new starting index (`new_first`). If `new_first` is less
        than the current `first`, new elements are prepended. If `new_first` is
        greater than the current `last`, the list is cleared. Otherwise, elements
        are removed from the beginning of the list to match the new range.

        Args:
            nodes: A dictionary mapping text numbers to lists of elements.
            anchor_word_list: A reference to the anchor word list.
            new_first: The new starting index for the range.
            text_number: The identifier for the text being processed.
        """
        if new_first < self.first:
            more = []
            for count in range(self.first - new_first):
                index = new_first + count
                text = nodes[text_number][index].text
                more.append(ElementInfo(anchor_word_list, text, text_number, index))
            self.element_info = more + self.element_info
            self.first = new_first
        elif new_first > self.last:
            self.element_info.clear()
            self.first = new_first
            self.last = self.first - 1
        else:
            for _ in range(new_first - self.first):
                self.element_info.pop(0)
            self.first = new_first

    def set_last(
        self,
        nodes: dict[int, list[AElement]],
        anchor_word_list: AnchorWordList,
        new_last: int,
        text_number: int,
    ) -> None:
        """Adjusts the range of elements tracked by updating the `last` index.

        This method modifies the `element_info` list and updates the `last`
        index based on the provided `new_last` value. It ensures that the
        range of elements between `first` and `last` is consistent and
        handles cases where `new_last` is greater, less than, or within
        the current range.

        Args:
            nodes: A dictionary mapping text numbers to lists of elements.
            anchor_word_list: A reference to the anchor word list.
            new_last: The new value for the `last` index.
            text_number: The identifier for the text being processed.

        Raises:
            EndOfTextExceptionError: If `new_last` exceeds the available
            elements in the specified text.
        """
        if new_last > self.last:
            for count in range(new_last - self.last):
                index = self.last + count + 1

                if index >= len(nodes[text_number]):
                    raise EndOfTextExceptionError()

                text = nodes[text_number][index].text

                self.element_info.append(
                    ElementInfo(anchor_word_list, text, text_number, index)
                )
            self.last = new_last
        elif new_last < self.first:
            self.element_info.clear()
            self.first = new_last
            self.last = self.first - 1
        else:
            for _ in range(self.last - new_last):
                self.element_info.pop()

            self.last = new_last
