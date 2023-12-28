class AElement:
    def __init__(self, node, element_number):
        self.element = node
        self.element_number = element_number
        self.alignment_number = -1
        self.length = len(self.element.text)
