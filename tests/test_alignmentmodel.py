from typing import List

from lxml import etree

from python_tca2 import alignmentmodel
from python_tca2.aelement import AElement
from python_tca2.aligned import Aligned
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


def test_suggest1():
    trees = [
        etree.fromstring(
            """
    <document>
      <s id="1">Kanskje en innkjøpsordning for kvenskspråklig litteratur.</s>
      <s id="2">Utvikling av undervisnings- og lærematerialer.</s>
    </document>
    """
        ),
        etree.fromstring(
            """
    <document>
      <s id="1">Kvääninkielinen litteratuuri osto-oorninkhiin piian.</s>
      <s id="2">Opetus- ja oppimateriaaliitten kehittäminen.</s>
    </document>
    """
        ),
    ]

    model = alignmentmodel.AlignmentModel()
    load_text(trees, model)

    model.suggets_without_gui()

    alignments: List[Link] = [Link(), Link()]
    alignments[0].element_numbers = [[0], [0]]
    alignments[0].alignment_number = 0
    alignments[1].element_numbers = [[1], [1]]
    alignments[1].alignment_number = 1

    elements: List[List[AElement]] = [
        [
            AElement(model.nodes[0][0], 0),
            AElement(model.nodes[0][1], 1),
        ],
        [
            AElement(model.nodes[1][0], 0),
            AElement(model.nodes[1][1], 1),
        ],
    ]
    elements[0][0].alignment_number = 0
    elements[0][1].alignment_number = 1
    elements[1][0].alignment_number = 0
    elements[1][1].alignment_number = 1

    aligned = Aligned()
    aligned.alignments = alignments
    aligned.elements = elements

    assert model.aligned == aligned


def test_suggest2():
    trees = [
        etree.fromstring(
            """
<document>
  <s id="74">Når folk har gått på nybegynnerkursene hos enten instituttet eller universitetet, kan man tilby dem muligheten å få en mentor som de kan snakke kvensk med og gjøre aktiviteter med på kvensk.</s>
  <s id="75">Motivere folk til å lære kvensk og vise dem at man får jobb med det, og at det er nok arbeid til alle.</s>
  <s id="77">Forsøke selv å være gode forbilder.</s>
</document>
"""  # noqa: E501
        ),
        etree.fromstring(
            """
<document>
  <s id="78">Ko ihmiset oon käynheet institutin tahi universiteetin alkukurssin, niin heile tarjothaan maholisuuen saaja menttorin, jonka kans puhhuut ja tehhä assiita kvääniksi  Motiveerata ihmissii siihen ette oppiit kväänin kieltä ja näyttäät heile ette sillä saapi työn ja ette työtä oon nokko kaikile.</s>
  <s id="80">Freistata itte olla hyvät esikuvat.</s>
</document>
"""  # noqa: E501
        ),
    ]

    model = alignmentmodel.AlignmentModel()
    load_text(trees, model)

    model.suggets_without_gui()

    model.aligned.to_json()
    assert model.aligned.to_json() == {
        "elements": [
            [
                {
                    "element": "Når folk har gått på nybegynnerkursene hos enten instituttet eller universitetet, kan man tilby dem muligheten å få en mentor som de kan snakke kvensk med og gjøre aktiviteter med på kvensk.",  # noqa: E501
                    "element_number": 0,
                    "alignment_number": 0,
                    "length": 190,
                },
                {
                    "element": "Motivere folk til å lære kvensk og vise dem at man får jobb med det, og at det er nok arbeid til alle.",  # noqa: E501
                    "element_number": 1,
                    "alignment_number": 0,
                    "length": 102,
                },
                {
                    "element": "Forsøke selv å være gode forbilder.",
                    "element_number": 2,
                    "alignment_number": 1,
                    "length": 35,
                },
            ],
            [
                {
                    "element": "Ko ihmiset oon käynheet institutin tahi universiteetin alkukurssin, niin heile tarjothaan maholisuuen saaja menttorin, jonka kans puhhuut ja tehhä assiita kvääniksi  Motiveerata ihmissii siihen ette oppiit kväänin kieltä ja näyttäät heile ette sillä saapi työn ja ette työtä oon nokko kaikile.",  # noqa: E501
                    "element_number": 0,
                    "alignment_number": 0,
                    "length": 293,
                },
                {
                    "element": "Freistata itte olla hyvät esikuvat.",
                    "element_number": 1,
                    "alignment_number": 1,
                    "length": 35,
                },
            ],
        ],
        "alignments": [
            {"alignment_number": 0, "element_numbers": [[0, 1], [0]]},
            {"alignment_number": 1, "element_numbers": [[2], [1]]},
        ],
    }
