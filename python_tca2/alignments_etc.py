from collections import defaultdict

from python_tca2.aelement import AElement


class AlignmentsEtc:
    def __init__(self):
        self.elements: defaultdict[int, list[AElement]] = defaultdict(list)

    def to_json(self):
        return {
            "elements": [
                [lang_element.to_json() for lang_element in lang_elements]
                for lang_elements in self.elements.values()
            ],
        }

    def to_tuple(self):
        return tuple(
            " ".join([aelement.text for aelement in aelements])
            for aelements in self.elements.values()
        )
