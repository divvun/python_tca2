class Unaligned:
    def __init__(self):
        self.elements = [[], []]

    def pop(self, t):
        return self.elements[t].pop()

    def add(self, t, element):
        self.elements[t].append(element)
