from typing import List

from lxml import etree

from python_tca2 import alignmentmodel
from python_tca2.aelement import AElement
from python_tca2.aligned import Aligned
from python_tca2.anchorwordlistentry import AnchorWordListEntry
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


def load_anchor_words():
    anchor_words = """1* / 1*, okta, ovtta
mill, million* / milj, miljovdna*, miljovnna*
Sametinget* / Sámedigg*, Sámedikk*
"""
    anchor_word_list = alignmentmodel.AnchorWordList()
    anchor_word_list.entries = [
        AnchorWordListEntry(line.strip()) for line in anchor_words.splitlines()
    ]

    return anchor_word_list


# Set a bench for alignments using anchor words
def test_anchor1():
    trees = [
        etree.fromstring(
            """
    <document>
        <s id="1">1 million kroner til landbruket i arktisk</s>
        <s id="2">27. juni 2014</s>
        <s id="3">Sametingsrådet har bevilget 1 millioner kroner til Arktisk landbruk i nord.</s>
    </document>
    """  # noqa: E501
        ),
        etree.fromstring(
            """
    <document>
        <s id="1">1 miljon ruvnno árktalaš eanadollui</s>
        <s id="2">27. Geassemánnu 2014</s>
        <s id="3">Sámediggeráđđi lea juolludan 1 miljon ruvnno árktalaš eanadollui davvin.</s>
    </document>
    """  # noqa: E501
        ),
    ]

    model = alignmentmodel.AlignmentModel()
    load_text(trees, model)
    model.anchor_word_list = load_anchor_words()

    model.suggets_without_gui()

    assert model.compare.to_json() == {
        "elements_info": [
            {
                "first": 0,
                "last": 2,
                "element_info": [
                    {
                        "element_number": 0,
                        "length": 41,
                        "num_words": 7,
                        "words": [
                            "1",
                            "million",
                            "kroner",
                            "til",
                            "landbruket",
                            "i",
                            "arktisk",
                        ],
                        "anchor_word_hits": [
                            {
                                "index": 0,
                                "element_number": 0,
                                "pos": 0,
                                "word": "1",
                            },
                            {
                                "index": 1,
                                "element_number": 0,
                                "pos": 1,
                                "word": "million",
                            },
                        ],
                        "scoring_characters": "",
                        "proper_names": [],
                    },
                    {
                        "element_number": 1,
                        "length": 13,
                        "num_words": 3,
                        "words": ["27", "juni", "2014"],
                        "anchor_word_hits": [],
                        "scoring_characters": "",
                        "proper_names": [],
                    },
                    {
                        "element_number": 2,
                        "length": 75,
                        "num_words": 11,
                        "words": [
                            "Sametingsrådet",
                            "har",
                            "bevilget",
                            "1",
                            "millioner",
                            "kroner",
                            "til",
                            "Arktisk",
                            "landbruk",
                            "i",
                            "nord",
                        ],
                        "anchor_word_hits": [
                            {
                                "index": 0,
                                "element_number": 2,
                                "pos": 3,
                                "word": "1",
                            },
                            {
                                "index": 1,
                                "element_number": 2,
                                "pos": 4,
                                "word": "millioner",
                            },
                        ],
                        "scoring_characters": "",
                        "proper_names": ["Sametingsrådet", "Arktisk"],
                    },
                ],
            },
            {
                "first": 0,
                "last": 2,
                "element_info": [
                    {
                        "element_number": 0,
                        "length": 35,
                        "num_words": 5,
                        "words": ["1", "miljon", "ruvnno", "árktalaš", "eanadollui"],
                        "anchor_word_hits": [
                            {"index": 0, "element_number": 0, "pos": 0, "word": "1"}
                        ],
                        "scoring_characters": "",
                        "proper_names": [],
                    },
                    {
                        "element_number": 1,
                        "length": 20,
                        "num_words": 3,
                        "words": ["27", "Geassemánnu", "2014"],
                        "anchor_word_hits": [],
                        "scoring_characters": "",
                        "proper_names": ["Geassemánnu"],
                    },
                    {
                        "element_number": 2,
                        "length": 72,
                        "num_words": 9,
                        "words": [
                            "Sámediggeráđđi",
                            "lea",
                            "juolludan",
                            "1",
                            "miljon",
                            "ruvnno",
                            "árktalaš",
                            "eanadollui",
                            "davvin",
                        ],
                        "anchor_word_hits": [
                            {
                                "index": 0,
                                "element_number": 2,
                                "pos": 3,
                                "word": "1",
                            },
                            {
                                "index": 2,
                                "element_number": 2,
                                "pos": 0,
                                "word": "Sámediggeráđđi",
                            },
                        ],
                        "scoring_characters": "",
                        "proper_names": ["Sámediggeráđđi"],
                    },
                ],
            },
        ],
        "matrix": {
            "cells": {
                "0,0,-1,0": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [],
                            [
                                {
                                    "element_number": 0,
                                    "length": 35,
                                    "num_words": 5,
                                    "words": [
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        }
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "0,0,0,-1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 0,
                                    "length": 41,
                                    "num_words": 7,
                                    "words": [
                                        "1",
                                        "million",
                                        "kroner",
                                        "til",
                                        "landbruket",
                                        "i",
                                        "arktisk",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 0,
                                            "pos": 1,
                                            "word": "million",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                            [],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "0,0,0,0": {
                    "element_info_to_be_compared": {
                        "score": 4.0,
                        "common_clusters": {
                            "clusters": [
                                {
                                    "refs": [
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "length": 1,
                                            "word": "1",
                                        },
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 1,
                                            "element_number": 0,
                                            "pos": 0,
                                            "length": 1,
                                            "word": "1",
                                        },
                                    ]
                                }
                            ]
                        },
                        "info": [
                            [
                                {
                                    "element_number": 0,
                                    "length": 41,
                                    "num_words": 7,
                                    "words": [
                                        "1",
                                        "million",
                                        "kroner",
                                        "til",
                                        "landbruket",
                                        "i",
                                        "arktisk",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 0,
                                            "pos": 1,
                                            "word": "million",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                            [
                                {
                                    "element_number": 0,
                                    "length": 35,
                                    "num_words": 5,
                                    "words": [
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        }
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "0,0,0,1": {
                    "element_info_to_be_compared": {
                        "score": 4.999,
                        "common_clusters": {
                            "clusters": [
                                {
                                    "refs": [
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "length": 1,
                                            "word": "1",
                                        },
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 1,
                                            "element_number": 0,
                                            "pos": 0,
                                            "length": 1,
                                            "word": "1",
                                        },
                                    ]
                                }
                            ]
                        },
                        "info": [
                            [
                                {
                                    "element_number": 0,
                                    "length": 41,
                                    "num_words": 7,
                                    "words": [
                                        "1",
                                        "million",
                                        "kroner",
                                        "til",
                                        "landbruket",
                                        "i",
                                        "arktisk",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 0,
                                            "pos": 1,
                                            "word": "million",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                            [
                                {
                                    "element_number": 0,
                                    "length": 35,
                                    "num_words": 5,
                                    "words": [
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        }
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                },
                                {
                                    "element_number": 1,
                                    "length": 20,
                                    "num_words": 3,
                                    "words": ["27", "Geassemánnu", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": ["Geassemánnu"],
                                },
                            ],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "0,0,1,0": {
                    "element_info_to_be_compared": {
                        "score": -99999.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 0,
                                    "length": 41,
                                    "num_words": 7,
                                    "words": [
                                        "1",
                                        "million",
                                        "kroner",
                                        "til",
                                        "landbruket",
                                        "i",
                                        "arktisk",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 0,
                                            "pos": 1,
                                            "word": "million",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                },
                                {
                                    "element_number": 1,
                                    "length": 13,
                                    "num_words": 3,
                                    "words": ["27", "juni", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                },
                            ],
                            [
                                {
                                    "element_number": 0,
                                    "length": 35,
                                    "num_words": 5,
                                    "words": [
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        }
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "0,1,-1,1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [],
                            [
                                {
                                    "element_number": 1,
                                    "length": 20,
                                    "num_words": 3,
                                    "words": ["27", "Geassemánnu", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": ["Geassemánnu"],
                                }
                            ],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "0,1,0,0": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 0,
                                    "length": 41,
                                    "num_words": 7,
                                    "words": [
                                        "1",
                                        "million",
                                        "kroner",
                                        "til",
                                        "landbruket",
                                        "i",
                                        "arktisk",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 0,
                                            "pos": 1,
                                            "word": "million",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                            [],
                        ],
                    },
                    "best_path_score": 4.0,
                },
                "0,1,0,1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 0,
                                    "length": 41,
                                    "num_words": 7,
                                    "words": [
                                        "1",
                                        "million",
                                        "kroner",
                                        "til",
                                        "landbruket",
                                        "i",
                                        "arktisk",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 0,
                                            "pos": 1,
                                            "word": "million",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                            [
                                {
                                    "element_number": 1,
                                    "length": 20,
                                    "num_words": 3,
                                    "words": ["27", "Geassemánnu", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": ["Geassemánnu"],
                                }
                            ],
                        ],
                    },
                    "best_path_score": 4.999,
                },
                "0,1,0,2": {
                    "element_info_to_be_compared": {
                        "score": -99999.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 0,
                                    "length": 41,
                                    "num_words": 7,
                                    "words": [
                                        "1",
                                        "million",
                                        "kroner",
                                        "til",
                                        "landbruket",
                                        "i",
                                        "arktisk",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 0,
                                            "pos": 1,
                                            "word": "million",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                            [
                                {
                                    "element_number": 1,
                                    "length": 20,
                                    "num_words": 3,
                                    "words": ["27", "Geassemánnu", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": ["Geassemánnu"],
                                },
                                {
                                    "element_number": 2,
                                    "length": 72,
                                    "num_words": 9,
                                    "words": [
                                        "Sámediggeráđđi",
                                        "lea",
                                        "juolludan",
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                        "davvin",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 2,
                                            "element_number": 2,
                                            "pos": 0,
                                            "word": "Sámediggeráđđi",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sámediggeráđđi"],
                                },
                            ],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "0,1,1,1": {
                    "element_info_to_be_compared": {
                        "score": -99999.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 0,
                                    "length": 41,
                                    "num_words": 7,
                                    "words": [
                                        "1",
                                        "million",
                                        "kroner",
                                        "til",
                                        "landbruket",
                                        "i",
                                        "arktisk",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 0,
                                            "pos": 1,
                                            "word": "million",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                },
                                {
                                    "element_number": 1,
                                    "length": 13,
                                    "num_words": 3,
                                    "words": ["27", "juni", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                },
                            ],
                            [
                                {
                                    "element_number": 1,
                                    "length": 20,
                                    "num_words": 3,
                                    "words": ["27", "Geassemánnu", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": ["Geassemánnu"],
                                }
                            ],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "0,2,-1,2": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [],
                            [
                                {
                                    "element_number": 2,
                                    "length": 72,
                                    "num_words": 9,
                                    "words": [
                                        "Sámediggeráđđi",
                                        "lea",
                                        "juolludan",
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                        "davvin",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 2,
                                            "element_number": 2,
                                            "pos": 0,
                                            "word": "Sámediggeráđđi",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sámediggeráđđi"],
                                }
                            ],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "0,2,0,1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 0,
                                    "length": 41,
                                    "num_words": 7,
                                    "words": [
                                        "1",
                                        "million",
                                        "kroner",
                                        "til",
                                        "landbruket",
                                        "i",
                                        "arktisk",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 0,
                                            "pos": 1,
                                            "word": "million",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                            [],
                        ],
                    },
                    "best_path_score": 4.999,
                },
                "0,2,0,2": {
                    "element_info_to_be_compared": {
                        "score": 3.0,
                        "common_clusters": {
                            "clusters": [
                                {
                                    "refs": [
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "length": 1,
                                            "word": "1",
                                        },
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 1,
                                            "element_number": 2,
                                            "pos": 3,
                                            "length": 1,
                                            "word": "1",
                                        },
                                    ]
                                }
                            ]
                        },
                        "info": [
                            [
                                {
                                    "element_number": 0,
                                    "length": 41,
                                    "num_words": 7,
                                    "words": [
                                        "1",
                                        "million",
                                        "kroner",
                                        "til",
                                        "landbruket",
                                        "i",
                                        "arktisk",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 0,
                                            "pos": 1,
                                            "word": "million",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                            [
                                {
                                    "element_number": 2,
                                    "length": 72,
                                    "num_words": 9,
                                    "words": [
                                        "Sámediggeráđđi",
                                        "lea",
                                        "juolludan",
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                        "davvin",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 2,
                                            "element_number": 2,
                                            "pos": 0,
                                            "word": "Sámediggeráđđi",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sámediggeráđđi"],
                                }
                            ],
                        ],
                    },
                    "best_path_score": 4.999,
                },
                "0,2,1,2": {
                    "element_info_to_be_compared": {
                        "score": 4.999,
                        "common_clusters": {
                            "clusters": [
                                {
                                    "refs": [
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "length": 1,
                                            "word": "1",
                                        },
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 1,
                                            "element_number": 2,
                                            "pos": 3,
                                            "length": 1,
                                            "word": "1",
                                        },
                                    ]
                                }
                            ]
                        },
                        "info": [
                            [
                                {
                                    "element_number": 0,
                                    "length": 41,
                                    "num_words": 7,
                                    "words": [
                                        "1",
                                        "million",
                                        "kroner",
                                        "til",
                                        "landbruket",
                                        "i",
                                        "arktisk",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 0,
                                            "pos": 1,
                                            "word": "million",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                },
                                {
                                    "element_number": 1,
                                    "length": 13,
                                    "num_words": 3,
                                    "words": ["27", "juni", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                },
                            ],
                            [
                                {
                                    "element_number": 2,
                                    "length": 72,
                                    "num_words": 9,
                                    "words": [
                                        "Sámediggeráđđi",
                                        "lea",
                                        "juolludan",
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                        "davvin",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 2,
                                            "element_number": 2,
                                            "pos": 0,
                                            "word": "Sámediggeráđđi",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sámediggeráđđi"],
                                }
                            ],
                        ],
                    },
                    "best_path_score": 4.999,
                },
                "0,3,0,2": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 0,
                                    "length": 41,
                                    "num_words": 7,
                                    "words": [
                                        "1",
                                        "million",
                                        "kroner",
                                        "til",
                                        "landbruket",
                                        "i",
                                        "arktisk",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 0,
                                            "pos": 1,
                                            "word": "million",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                            [],
                        ],
                    },
                    "best_path_score": 4.999,
                },
                "1,0,0,0": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [],
                            [
                                {
                                    "element_number": 0,
                                    "length": 35,
                                    "num_words": 5,
                                    "words": [
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        }
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                        ],
                    },
                    "best_path_score": 4.0,
                },
                "1,0,1,-1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 1,
                                    "length": 13,
                                    "num_words": 3,
                                    "words": ["27", "juni", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                            [],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "1,0,1,0": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 1,
                                    "length": 13,
                                    "num_words": 3,
                                    "words": ["27", "juni", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                            [
                                {
                                    "element_number": 0,
                                    "length": 35,
                                    "num_words": 5,
                                    "words": [
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        }
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "1,0,1,1": {
                    "element_info_to_be_compared": {
                        "score": -99999.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 1,
                                    "length": 13,
                                    "num_words": 3,
                                    "words": ["27", "juni", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                            [
                                {
                                    "element_number": 0,
                                    "length": 35,
                                    "num_words": 5,
                                    "words": [
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        }
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                },
                                {
                                    "element_number": 1,
                                    "length": 20,
                                    "num_words": 3,
                                    "words": ["27", "Geassemánnu", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": ["Geassemánnu"],
                                },
                            ],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "1,0,2,0": {
                    "element_info_to_be_compared": {
                        "score": -99999.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 1,
                                    "length": 13,
                                    "num_words": 3,
                                    "words": ["27", "juni", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                },
                                {
                                    "element_number": 2,
                                    "length": 75,
                                    "num_words": 11,
                                    "words": [
                                        "Sametingsrådet",
                                        "har",
                                        "bevilget",
                                        "1",
                                        "millioner",
                                        "kroner",
                                        "til",
                                        "Arktisk",
                                        "landbruk",
                                        "i",
                                        "nord",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 2,
                                            "pos": 4,
                                            "word": "millioner",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sametingsrådet", "Arktisk"],
                                },
                            ],
                            [
                                {
                                    "element_number": 0,
                                    "length": 35,
                                    "num_words": 5,
                                    "words": [
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        }
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "1,1,0,1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [],
                            [
                                {
                                    "element_number": 1,
                                    "length": 20,
                                    "num_words": 3,
                                    "words": ["27", "Geassemánnu", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": ["Geassemánnu"],
                                }
                            ],
                        ],
                    },
                    "best_path_score": 4.999,
                },
                "1,1,1,0": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 1,
                                    "length": 13,
                                    "num_words": 3,
                                    "words": ["27", "juni", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                            [],
                        ],
                    },
                    "best_path_score": 0.0,
                },
                "1,1,1,1": {
                    "element_info_to_be_compared": {
                        "score": 7.0,
                        "common_clusters": {
                            "clusters": [
                                {
                                    "refs": [
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 0,
                                            "element_number": 1,
                                            "pos": 0,
                                            "length": 1,
                                            "word": "27",
                                        },
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 1,
                                            "element_number": 1,
                                            "pos": 0,
                                            "length": 1,
                                            "word": "27",
                                        },
                                    ]
                                },
                                {
                                    "refs": [
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 0,
                                            "element_number": 1,
                                            "pos": 2,
                                            "length": 1,
                                            "word": "2014",
                                        },
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 1,
                                            "element_number": 1,
                                            "pos": 2,
                                            "length": 1,
                                            "word": "2014",
                                        },
                                    ]
                                },
                            ]
                        },
                        "info": [
                            [
                                {
                                    "element_number": 1,
                                    "length": 13,
                                    "num_words": 3,
                                    "words": ["27", "juni", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                            [
                                {
                                    "element_number": 1,
                                    "length": 20,
                                    "num_words": 3,
                                    "words": ["27", "Geassemánnu", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": ["Geassemánnu"],
                                }
                            ],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "1,1,1,2": {
                    "element_info_to_be_compared": {
                        "score": -99999.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 1,
                                    "length": 13,
                                    "num_words": 3,
                                    "words": ["27", "juni", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                            [
                                {
                                    "element_number": 1,
                                    "length": 20,
                                    "num_words": 3,
                                    "words": ["27", "Geassemánnu", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": ["Geassemánnu"],
                                },
                                {
                                    "element_number": 2,
                                    "length": 72,
                                    "num_words": 9,
                                    "words": [
                                        "Sámediggeráđđi",
                                        "lea",
                                        "juolludan",
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                        "davvin",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 2,
                                            "element_number": 2,
                                            "pos": 0,
                                            "word": "Sámediggeráđđi",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sámediggeráđđi"],
                                },
                            ],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "1,1,2,1": {
                    "element_info_to_be_compared": {
                        "score": -99999.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 1,
                                    "length": 13,
                                    "num_words": 3,
                                    "words": ["27", "juni", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                },
                                {
                                    "element_number": 2,
                                    "length": 75,
                                    "num_words": 11,
                                    "words": [
                                        "Sametingsrådet",
                                        "har",
                                        "bevilget",
                                        "1",
                                        "millioner",
                                        "kroner",
                                        "til",
                                        "Arktisk",
                                        "landbruk",
                                        "i",
                                        "nord",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 2,
                                            "pos": 4,
                                            "word": "millioner",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sametingsrådet", "Arktisk"],
                                },
                            ],
                            [
                                {
                                    "element_number": 1,
                                    "length": 20,
                                    "num_words": 3,
                                    "words": ["27", "Geassemánnu", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": ["Geassemánnu"],
                                }
                            ],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "1,2,0,2": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [],
                            [
                                {
                                    "element_number": 2,
                                    "length": 72,
                                    "num_words": 9,
                                    "words": [
                                        "Sámediggeráđđi",
                                        "lea",
                                        "juolludan",
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                        "davvin",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 2,
                                            "element_number": 2,
                                            "pos": 0,
                                            "word": "Sámediggeráđđi",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sámediggeráđđi"],
                                }
                            ],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "1,2,1,1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 1,
                                    "length": 13,
                                    "num_words": 3,
                                    "words": ["27", "juni", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                            [],
                        ],
                    },
                    "best_path_score": 11.0,
                },
                "1,2,1,2": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 1,
                                    "length": 13,
                                    "num_words": 3,
                                    "words": ["27", "juni", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                            [
                                {
                                    "element_number": 2,
                                    "length": 72,
                                    "num_words": 9,
                                    "words": [
                                        "Sámediggeráđđi",
                                        "lea",
                                        "juolludan",
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                        "davvin",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 2,
                                            "element_number": 2,
                                            "pos": 0,
                                            "word": "Sámediggeráđđi",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sámediggeráđđi"],
                                }
                            ],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "1,2,2,2": {
                    "element_info_to_be_compared": {
                        "score": 3.999,
                        "common_clusters": {
                            "clusters": [
                                {
                                    "refs": [
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "length": 1,
                                            "word": "1",
                                        },
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 1,
                                            "element_number": 2,
                                            "pos": 3,
                                            "length": 1,
                                            "word": "1",
                                        },
                                    ]
                                }
                            ]
                        },
                        "info": [
                            [
                                {
                                    "element_number": 1,
                                    "length": 13,
                                    "num_words": 3,
                                    "words": ["27", "juni", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                },
                                {
                                    "element_number": 2,
                                    "length": 75,
                                    "num_words": 11,
                                    "words": [
                                        "Sametingsrådet",
                                        "har",
                                        "bevilget",
                                        "1",
                                        "millioner",
                                        "kroner",
                                        "til",
                                        "Arktisk",
                                        "landbruk",
                                        "i",
                                        "nord",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 2,
                                            "pos": 4,
                                            "word": "millioner",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sametingsrådet", "Arktisk"],
                                },
                            ],
                            [
                                {
                                    "element_number": 2,
                                    "length": 72,
                                    "num_words": 9,
                                    "words": [
                                        "Sámediggeráđđi",
                                        "lea",
                                        "juolludan",
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                        "davvin",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 2,
                                            "element_number": 2,
                                            "pos": 0,
                                            "word": "Sámediggeráđđi",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sámediggeráđđi"],
                                }
                            ],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "1,3,1,2": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 1,
                                    "length": 13,
                                    "num_words": 3,
                                    "words": ["27", "juni", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                            [],
                        ],
                    },
                    "best_path_score": 11.0,
                },
                "2,0,1,0": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [],
                            [
                                {
                                    "element_number": 0,
                                    "length": 35,
                                    "num_words": 5,
                                    "words": [
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        }
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                        ],
                    },
                    "best_path_score": 4.0,
                },
                "2,0,2,-1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 2,
                                    "length": 75,
                                    "num_words": 11,
                                    "words": [
                                        "Sametingsrådet",
                                        "har",
                                        "bevilget",
                                        "1",
                                        "millioner",
                                        "kroner",
                                        "til",
                                        "Arktisk",
                                        "landbruk",
                                        "i",
                                        "nord",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 2,
                                            "pos": 4,
                                            "word": "millioner",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sametingsrådet", "Arktisk"],
                                }
                            ],
                            [],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "2,0,2,0": {
                    "element_info_to_be_compared": {
                        "score": 3.0,
                        "common_clusters": {
                            "clusters": [
                                {
                                    "refs": [
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "length": 1,
                                            "word": "1",
                                        },
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 1,
                                            "element_number": 0,
                                            "pos": 0,
                                            "length": 1,
                                            "word": "1",
                                        },
                                    ]
                                }
                            ]
                        },
                        "info": [
                            [
                                {
                                    "element_number": 2,
                                    "length": 75,
                                    "num_words": 11,
                                    "words": [
                                        "Sametingsrådet",
                                        "har",
                                        "bevilget",
                                        "1",
                                        "millioner",
                                        "kroner",
                                        "til",
                                        "Arktisk",
                                        "landbruk",
                                        "i",
                                        "nord",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 2,
                                            "pos": 4,
                                            "word": "millioner",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sametingsrådet", "Arktisk"],
                                }
                            ],
                            [
                                {
                                    "element_number": 0,
                                    "length": 35,
                                    "num_words": 5,
                                    "words": [
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        }
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "2,0,2,1": {
                    "element_info_to_be_compared": {
                        "score": 2.999,
                        "common_clusters": {
                            "clusters": [
                                {
                                    "refs": [
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "length": 1,
                                            "word": "1",
                                        },
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 1,
                                            "element_number": 0,
                                            "pos": 0,
                                            "length": 1,
                                            "word": "1",
                                        },
                                    ]
                                }
                            ]
                        },
                        "info": [
                            [
                                {
                                    "element_number": 2,
                                    "length": 75,
                                    "num_words": 11,
                                    "words": [
                                        "Sametingsrådet",
                                        "har",
                                        "bevilget",
                                        "1",
                                        "millioner",
                                        "kroner",
                                        "til",
                                        "Arktisk",
                                        "landbruk",
                                        "i",
                                        "nord",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 2,
                                            "pos": 4,
                                            "word": "millioner",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sametingsrådet", "Arktisk"],
                                }
                            ],
                            [
                                {
                                    "element_number": 0,
                                    "length": 35,
                                    "num_words": 5,
                                    "words": [
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        }
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                },
                                {
                                    "element_number": 1,
                                    "length": 20,
                                    "num_words": 3,
                                    "words": ["27", "Geassemánnu", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": ["Geassemánnu"],
                                },
                            ],
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "2,1,1,1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [],
                            [
                                {
                                    "element_number": 1,
                                    "length": 20,
                                    "num_words": 3,
                                    "words": ["27", "Geassemánnu", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": ["Geassemánnu"],
                                }
                            ],
                        ],
                    },
                    "best_path_score": 11.0,
                },
                "2,1,2,0": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 2,
                                    "length": 75,
                                    "num_words": 11,
                                    "words": [
                                        "Sametingsrådet",
                                        "har",
                                        "bevilget",
                                        "1",
                                        "millioner",
                                        "kroner",
                                        "til",
                                        "Arktisk",
                                        "landbruk",
                                        "i",
                                        "nord",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 2,
                                            "pos": 4,
                                            "word": "millioner",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sametingsrådet", "Arktisk"],
                                }
                            ],
                            [],
                        ],
                    },
                    "best_path_score": 3.0,
                },
                "2,1,2,1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 2,
                                    "length": 75,
                                    "num_words": 11,
                                    "words": [
                                        "Sametingsrådet",
                                        "har",
                                        "bevilget",
                                        "1",
                                        "millioner",
                                        "kroner",
                                        "til",
                                        "Arktisk",
                                        "landbruk",
                                        "i",
                                        "nord",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 2,
                                            "pos": 4,
                                            "word": "millioner",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sametingsrådet", "Arktisk"],
                                }
                            ],
                            [
                                {
                                    "element_number": 1,
                                    "length": 20,
                                    "num_words": 3,
                                    "words": ["27", "Geassemánnu", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": ["Geassemánnu"],
                                }
                            ],
                        ],
                    },
                    "best_path_score": 2.999,
                },
                "2,1,2,2": {
                    "element_info_to_be_compared": {
                        "score": 4.999,
                        "common_clusters": {
                            "clusters": [
                                {
                                    "refs": [
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "length": 1,
                                            "word": "1",
                                        },
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 1,
                                            "element_number": 2,
                                            "pos": 3,
                                            "length": 1,
                                            "word": "1",
                                        },
                                    ]
                                }
                            ]
                        },
                        "info": [
                            [
                                {
                                    "element_number": 2,
                                    "length": 75,
                                    "num_words": 11,
                                    "words": [
                                        "Sametingsrådet",
                                        "har",
                                        "bevilget",
                                        "1",
                                        "millioner",
                                        "kroner",
                                        "til",
                                        "Arktisk",
                                        "landbruk",
                                        "i",
                                        "nord",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 2,
                                            "pos": 4,
                                            "word": "millioner",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sametingsrådet", "Arktisk"],
                                }
                            ],
                            [
                                {
                                    "element_number": 1,
                                    "length": 20,
                                    "num_words": 3,
                                    "words": ["27", "Geassemánnu", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": ["Geassemánnu"],
                                },
                                {
                                    "element_number": 2,
                                    "length": 72,
                                    "num_words": 9,
                                    "words": [
                                        "Sámediggeráđđi",
                                        "lea",
                                        "juolludan",
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                        "davvin",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 2,
                                            "element_number": 2,
                                            "pos": 0,
                                            "word": "Sámediggeráđđi",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sámediggeráđđi"],
                                },
                            ],
                        ],
                    },
                    "best_path_score": 8.998,
                },
                "2,2,1,2": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [],
                            [
                                {
                                    "element_number": 2,
                                    "length": 72,
                                    "num_words": 9,
                                    "words": [
                                        "Sámediggeráđđi",
                                        "lea",
                                        "juolludan",
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                        "davvin",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 2,
                                            "element_number": 2,
                                            "pos": 0,
                                            "word": "Sámediggeráđđi",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sámediggeráđđi"],
                                }
                            ],
                        ],
                    },
                    "best_path_score": 4.999,
                },
                "2,2,2,1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 2,
                                    "length": 75,
                                    "num_words": 11,
                                    "words": [
                                        "Sametingsrådet",
                                        "har",
                                        "bevilget",
                                        "1",
                                        "millioner",
                                        "kroner",
                                        "til",
                                        "Arktisk",
                                        "landbruk",
                                        "i",
                                        "nord",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 2,
                                            "pos": 4,
                                            "word": "millioner",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sametingsrådet", "Arktisk"],
                                }
                            ],
                            [],
                        ],
                    },
                    "best_path_score": 4.0,
                },
                "2,2,2,2": {
                    "element_info_to_be_compared": {
                        "score": 5.0,
                        "common_clusters": {
                            "clusters": [
                                {
                                    "refs": [
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "length": 1,
                                            "word": "1",
                                        },
                                        {
                                            "match_type": -3,
                                            "weight": 3.0,
                                            "t": 1,
                                            "element_number": 2,
                                            "pos": 3,
                                            "length": 1,
                                            "word": "1",
                                        },
                                    ]
                                }
                            ]
                        },
                        "info": [
                            [
                                {
                                    "element_number": 2,
                                    "length": 75,
                                    "num_words": 11,
                                    "words": [
                                        "Sametingsrådet",
                                        "har",
                                        "bevilget",
                                        "1",
                                        "millioner",
                                        "kroner",
                                        "til",
                                        "Arktisk",
                                        "landbruk",
                                        "i",
                                        "nord",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 2,
                                            "pos": 4,
                                            "word": "millioner",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sametingsrådet", "Arktisk"],
                                }
                            ],
                            [
                                {
                                    "element_number": 2,
                                    "length": 72,
                                    "num_words": 9,
                                    "words": [
                                        "Sámediggeráđđi",
                                        "lea",
                                        "juolludan",
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                        "davvin",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 2,
                                            "element_number": 2,
                                            "pos": 0,
                                            "word": "Sámediggeráđđi",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sámediggeráđđi"],
                                }
                            ],
                        ],
                    },
                    "best_path_score": 8.998,
                },
                "2,3,2,2": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [
                                {
                                    "element_number": 2,
                                    "length": 75,
                                    "num_words": 11,
                                    "words": [
                                        "Sametingsrådet",
                                        "har",
                                        "bevilget",
                                        "1",
                                        "millioner",
                                        "kroner",
                                        "til",
                                        "Arktisk",
                                        "landbruk",
                                        "i",
                                        "nord",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 1,
                                            "element_number": 2,
                                            "pos": 4,
                                            "word": "millioner",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sametingsrådet", "Arktisk"],
                                }
                            ],
                            [],
                        ],
                    },
                    "best_path_score": 16.0,
                },
                "3,0,2,0": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [],
                            [
                                {
                                    "element_number": 0,
                                    "length": 35,
                                    "num_words": 5,
                                    "words": [
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 0,
                                            "pos": 0,
                                            "word": "1",
                                        }
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": [],
                                }
                            ],
                        ],
                    },
                    "best_path_score": 4.0,
                },
                "3,1,2,1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [],
                            [
                                {
                                    "element_number": 1,
                                    "length": 20,
                                    "num_words": 3,
                                    "words": ["27", "Geassemánnu", "2014"],
                                    "anchor_word_hits": [],
                                    "scoring_characters": "",
                                    "proper_names": ["Geassemánnu"],
                                }
                            ],
                        ],
                    },
                    "best_path_score": 11.0,
                },
                "3,2,2,2": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
                            [],
                            [
                                {
                                    "element_number": 2,
                                    "length": 72,
                                    "num_words": 9,
                                    "words": [
                                        "Sámediggeráđđi",
                                        "lea",
                                        "juolludan",
                                        "1",
                                        "miljon",
                                        "ruvnno",
                                        "árktalaš",
                                        "eanadollui",
                                        "davvin",
                                    ],
                                    "anchor_word_hits": [
                                        {
                                            "index": 0,
                                            "element_number": 2,
                                            "pos": 3,
                                            "word": "1",
                                        },
                                        {
                                            "index": 2,
                                            "element_number": 2,
                                            "pos": 0,
                                            "word": "Sámediggeráđđi",
                                        },
                                    ],
                                    "scoring_characters": "",
                                    "proper_names": ["Sámediggeráđđi"],
                                }
                            ],
                        ],
                    },
                    "best_path_score": 16.0,
                },
            },
            "best_path_scores": {
                "-1,0": -1.0,
                "0,-1": -1.0,
                "0,0": -1.0,
                "0,1": -1.0,
                "1,0": -1.0,
                "-1,1": -1.0,
                "0,2": -1.0,
                "1,1": -1.0,
                "1,-1": -1.0,
                "2,0": -1.0,
                "1,2": -1.0,
                "2,1": -1.0,
                "2,2": -1.0,
                "-1,2": -1.0,
                "2,-1": -1.0,
            },
        },
        "step_list": [
            {"increment": [0, 1]},
            {"increment": [1, 0]},
            {"increment": [1, 1]},
            {"increment": [1, 2]},
            {"increment": [2, 1]},
        ],
    }
