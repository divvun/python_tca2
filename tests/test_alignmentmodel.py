from lxml import etree

from python_tca2.aelement import AElement
from python_tca2.link import Link
from python_tca2.toalign import ToAlign
from python_tca2.unaligned import Unaligned


def load_text(trees, model):
    for t, tree in enumerate(trees):
        model.docs.append(tree)
        model.nodes.append(tree.xpath("//s"))
        for index, node in enumerate(tree.iter("s")):
            model.unaligned.add(AElement(node, index), t)


def test_toalign_pickup():
    tree = etree.fromstring(
        """
    <document>
      <s id="1">Kanskje en innkjøpsordning for kvenskspråklig litteratur.</s>
      <s id="2">Utvikling av undervisnings- og lærematerialer.</s>
    </document>
    """
    )

    unaligned = Unaligned()
    for index, node in enumerate(tree.iter("s")):
        unaligned.add(AElement(node, index), 0)

    to_align = ToAlign()
    for element in unaligned.elements[0]:
        to_align.pickup(0, element)

    elements = []
    for index, node in enumerate(tree.iter("s")):
        element = AElement(node, index)
        element.element_number = index
        element.alignment_number = 0
        elements.append(element)

    link = Link()
    link.element_numbers[0] = [0, 1]
    link.alignment_number = 0

    assert to_align.first_alignment_number == 0
    assert str(to_align.elements[0][0]) == str(elements[0])
    assert to_align.elements[0][1] == elements[1]
    assert str(link) == str(to_align.pending[0])
