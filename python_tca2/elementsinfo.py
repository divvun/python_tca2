from python_tca2.elementinfo import ElementInfo
from python_tca2.exceptions import EndOfTextExceptionError


class ElementsInfo:
    def __init__(self):
        # print_frame()
        self.first = 0
        self.last = -1
        self.element_info = []

    def get_element_info(self, model, element_number, t):
        # print_frame()
        if element_number < self.first:
            self.set_first(model, element_number, t)
        elif element_number > self.last:
            try:
                self.set_last(model, element_number, t)
            except EndOfTextExceptionError as e:
                raise e
        return self.element_info[element_number - self.first]

    def set_first(self, model, new_first, t):
        # print_frame()
        if new_first < self.first:
            more = []
            for count in range(self.first - new_first):
                index = new_first + count
                text = model.nodes[t].item(index).get_text_content()
                more.append(ElementInfo(model.anchor_word_list, text, t, index))
            self.element_info = more + self.element_info
            self.first = new_first
        elif new_first > self.last:
            self.element_info.clear()
            self.first = new_first
            self.last = self.first - 1
        else:
            for count in range(new_first - self.first):
                self.element_info.pop(0)
            self.first = new_first

    def set_last(self, model, new_last, t):
        # print_frame()
        if new_last > self.last:
            for count in range(new_last - self.last):
                index = self.last + count + 1

                if index >= len(model.nodes[t]):
                    raise EndOfTextExceptionError()

                text = model.nodes[t][index].text
                self.element_info.append(
                    ElementInfo(model.anchor_word_list, text, t, index)
                )
