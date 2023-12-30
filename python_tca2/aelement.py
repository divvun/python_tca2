from python_tca2.alignment_utils import print_frame


class AElement:
    def __init__(self, node, element_number):
        print_frame("__init__")
        self.element = node
        self.element_number = element_number
        self.alignment_number = -1
        self.length = len(self.element.text)

    def __str__(self):
        print_frame("__str__")
        return (
            "element_number="
            + str(self.element_number)
            + ";alignment_number="
            + str(self.alignment_number)
            + ";length="
            + str(self.length)
            + ";text="
            + self.element.text
        )
