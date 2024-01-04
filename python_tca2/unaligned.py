from python_tca2.aelement import AElement


class Unaligned:
    def __init__(self):
        # print_frame()
        self.elements = [[], []]

    def pop(self, t: int) -> AElement:
        # print_frame()
        return self.elements[t].pop(0)

    def add(self, element: AElement, t: int):
        # print_frame()
        self.elements[t].append(element)

    def __str__(self):
        return "\n".join(
            [str(element) for elements in self.elements for element in elements]
        )
