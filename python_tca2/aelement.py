class AElement:
    def __init__(self, node, element_number):
        # print_frame()
        self.element = node
        self.element_number = element_number
        self.alignment_number = -1
        self.length = len(self.element.text)

    def __eq__(self, other):
        return (
            self.element_number == other.element_number
            and self.alignment_number == other.alignment_number
            and self.length == other.length
            and self.element.text == other.element.text
        )

    def __str__(self):
        # print_frame()
        return (
            "element_number: "
            + str(self.element_number)
            + " alignment_number: "
            + str(self.alignment_number)
            + " length: "
            + str(self.length)
            + " text: "
            + self.element.text
        )
