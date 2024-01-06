from python_tca2.elementinfo import ElementInfo
from python_tca2.exceptions import EndOfTextExceptionError


class ElementsInfo:
    def __init__(self):
        # print_frame()
        self.first = 0
        self.last = -1
        self.element_info = []

    def __str__(self):
        temp = "{\n"
        temp += f"first: {self.first},\n"
        temp += f"last: {self.last},\n"
        temp += "elementInfo: [\n"
        temp += ",\n".join([str(element_info) for element_info in self.element_info])
        temp += "]\n}\n"
        return temp

    def get_element_info(self, model, element_number, t):
        # print_frame()
        if element_number < self.first:
            self.set_first(model, element_number, t)
        elif element_number > self.last:
            self.set_last(model, element_number, t)
        print(
            f"element_number = {element_number}, first = {self.first}, "
            f"last = {self.last}"
        )
        return self.element_info[element_number - self.first]

    def set_first(self, model, new_first, t):
        print(f"setFirst: newFirst = {new_first}, t = {t}")
        if new_first < self.first:
            print("newFirst < first")
            more = []
            for count in range(self.first - new_first):
                index = new_first + count
                text = model.nodes[t][index].text
                print(f"index = {index}, text = {text}")
                more.append(ElementInfo(model.anchor_word_list, text, t, index))
            self.element_info = more + self.element_info
            print(f"elementInfo = {len(self.element_info)}")
            self.first = new_first
        elif new_first > self.last:
            print("newFirst > last")
            self.element_info.clear()
            self.first = new_first
            self.last = self.first - 1
        else:
            for count in range(new_first - self.first):
                self.element_info.pop(0)
            print(f"2 elementInfo = {len(self.element_info)} {new_first}")
            self.first = new_first

    def set_last(self, model, new_last, t):
        print(f"setLast: newLast = {new_last}, t = {t}")
        if new_last > self.last:
            print("newLast > last")
            for count in range(new_last - self.last):
                index = self.last + count + 1

                if index >= len(model.nodes[t]):
                    raise EndOfTextExceptionError()

                text = model.nodes[t][index].text
                self.element_info.append(
                    ElementInfo(model.anchor_word_list, text, t, index)
                )
