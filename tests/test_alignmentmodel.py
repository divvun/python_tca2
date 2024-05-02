from collections import defaultdict

from lxml import etree

from python_tca2 import alignmentmodel
from python_tca2.aelement import AElement
from python_tca2.aligned import Aligned
from python_tca2.alignments_etc import AlignmentsEtc
from python_tca2.anchorwordlist import AnchorWordList
from python_tca2.anchorwordlistentry import AnchorWordListEntry
from python_tca2.elementinfo import ElementInfo
from python_tca2.elementinfotobecompared import ElementInfoToBeCompared
from python_tca2.toalign import ToAlign
from python_tca2.unaligned import Unaligned


def test_get_score():
    """Test that the first if in find_dice_matches works as expected"""
    eitbc = ElementInfoToBeCompared()
    eitbc.add(element_info=ElementInfo(AnchorWordList(), "Mobil", 0, 0), t=0)
    eitbc.add(element_info=ElementInfo(AnchorWordList(), "Mobiila", 0, 0), t=1)

    assert eitbc.get_score() == 4.0


def test_alignment_etcs():
    alignment_etc = AlignmentsEtc(
        {
            0: [AElement("element0", 0), AElement("element1", 1)],
            1: [
                AElement("element2", 0),
                AElement("element3", 1),
                AElement("element4", 2),
            ],
        }
    )
    assert alignment_etc.to_tuple() == (
        "element0 element1",
        "element2 element3 element4",
    )


def test_find_dice_matches():
    """Test that the first if in find_dice_matches works as expected"""
    eitbc = ElementInfoToBeCompared()
    eitbc.add(element_info=ElementInfo(AnchorWordList(), "Mobil", 0, 0), t=0)
    eitbc.add(element_info=ElementInfo(AnchorWordList(), "Mobiila", 0, 0), t=1)
    eitbc.find_dice_matches(0, 1)

    assert eitbc.to_json() == {
        "score": 4.0,
        "common_clusters": {
            "clusters": [
                {
                    "refs": [
                        {
                            "match_type": -2,
                            "weight": 3.0,
                            "t": 0,
                            "element_number": 0,
                            "pos": 0,
                            "length": 1,
                            "word": "Mobil",
                        },
                        {
                            "match_type": -2,
                            "weight": 3.0,
                            "t": 1,
                            "element_number": 0,
                            "pos": 0,
                            "length": 1,
                            "word": "Mobiila",
                        },
                    ]
                }
            ]
        },
        "info": [
            {
                "element_number": 0,
                "length": 5,
                "num_words": 1,
                "words": ["Mobil"],
                "anchor_word_hits": [],
                "scoring_characters": "",
                "proper_names": ["Mobil"],
            },
            {
                "element_number": 0,
                "length": 7,
                "num_words": 1,
                "words": ["Mobiila"],
                "anchor_word_hits": [],
                "scoring_characters": "",
                "proper_names": ["Mobiila"],
            },
        ],
    }


def test_aelement_text():
    """Check that space is normalised in aelement.element"""
    node = etree.fromstring(
        '<s id="4">9 Økonomiske, administrative&#13; og miljømessige  konsekvenser</s>'
    )
    aelement = AElement(
        " ".join([text for text in "".join(node.itertext()).split() if text.strip()]), 0
    )

    assert aelement.text == "9 Økonomiske, administrative og miljømessige konsekvenser"


# A simple test of transfer from unaligned to toalign
def test_toalign_pickup():
    tree = etree.fromstring(
        """
    <document>
      <s id="1">Kanskje en innkjøpsordning for kvenskspråklig litteratur.</s>
      <s id="2">Utvikling av undervisnings- og lærematerialer.</s>
    </document>
    """
    )

    unaligned = Unaligned(
        elements={
            0: [
                AElement(
                    " ".join(
                        [
                            text
                            for text in "".join(node.itertext()).split()
                            if text.strip()
                        ]
                    ),
                    index,
                )
                for index, node in enumerate(tree.iter("s"))
            ],
            1: [],
        }
    )

    to_align = ToAlign(defaultdict(list))
    for element in unaligned.elements[0]:
        to_align.pickup(0, element)

    elements = []
    for index, node in enumerate(tree.iter("s")):
        element = AElement(
            " ".join(
                [text for text in "".join(node.itertext()).split() if text.strip()]
            ),
            index,
        )
        element.element_number = index
        elements.append(element)

    assert unaligned.to_json() == {
        "elements": [
            {
                "text": "Kanskje en innkjøpsordning for kvenskspråklig litteratur.",
                "element_number": 0,
            },
            {
                "text": "Utvikling av undervisnings- og lærematerialer.",
                "element_number": 1,
            },
        ]
    }

    assert to_align == ToAlign(
        {
            0: [
                AElement(
                    text="Kanskje en innkjøpsordning for kvenskspråklig litteratur.",
                    element_number=0,
                ),
                AElement(
                    text="Utvikling av undervisnings- og lærematerialer.",
                    element_number=1,
                ),
            ]
        }
    )


def test_aligned_to_text_file():
    aligned = Aligned([])
    a1 = AlignmentsEtc(
        {
            0: [],
            1: [
                AElement("Oslon tjïelte ( Oslon geažus -n ea genetiivageažus) .", 13),
            ],
        }
    )
    a2 = AlignmentsEtc(
        {
            0: [
                AElement(
                    "Aldri noensinne har språkuka og samiske språk fått så mye oppmerksomhet i samfunnet.",  # noqa: E501
                    5,
                )
            ],
            1: [
                AElement("Sámi giellavahkku", 14),
                AElement(
                    "Ii goassege leat Giellavahkku ja sámegielat ná bures fuomášuvvon servodagas.",  # noqa: E501
                    15,
                ),
            ],
        }
    )
    aligned.alignments = [
        a1,
        a2,
    ]
    assert aligned.valid_pairs() == [
        (
            "Aldri noensinne har språkuka og samiske språk fått så mye oppmerksomhet i samfunnet.",  # noqa: E501
            "Sámi giellavahkku Ii goassege leat Giellavahkku ja sámegielat ná bures fuomášuvvon servodagas.",  # noqa: E501
        ),
    ]


# A simple test of the alignment model
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

    model = alignmentmodel.AlignmentModel(keys=range(2))
    model.load_trees(trees)
    model.suggets_without_gui()

    assert model.aligned == Aligned(
        [
            AlignmentsEtc(
                {
                    0: [
                        AElement(
                            text="Kanskje en innkjøpsordning for kvenskspråklig litteratur.",
                            element_number=0,
                        )
                    ],
                    1: [
                        AElement(
                            text="Kvääninkielinen litteratuuri osto-oorninkhiin piian.",
                            element_number=0,
                        )
                    ],
                }
            ),
            AlignmentsEtc(
                {
                    0: [
                        AElement(
                            text="Utvikling av undervisnings- og lærematerialer.",
                            element_number=1,
                        )
                    ],
                    1: [
                        AElement(
                            text="Opetus- ja oppimateriaaliitten kehittäminen.",
                            element_number=1,
                        )
                    ],
                }
            ),
        ]
    )


# A test of the alignment model, with different number of sentences
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

    model = alignmentmodel.AlignmentModel(keys=range(2))
    model.load_trees(trees)
    model.suggets_without_gui()

    assert model.aligned == Aligned(
        [
            AlignmentsEtc(
                {
                    0: [
                        AElement(
                            text="Når folk har gått på nybegynnerkursene hos enten instituttet eller universitetet, kan man tilby dem muligheten å få en mentor som de kan snakke kvensk med og gjøre aktiviteter med på kvensk.",
                            element_number=0,
                        ),
                        AElement(
                            text="Motivere folk til å lære kvensk og vise dem at man får jobb med det, og at det er nok arbeid til alle.",
                            element_number=1,
                        ),
                    ],
                    1: [
                        AElement(
                            text="Ko ihmiset oon käynheet institutin tahi universiteetin alkukurssin, niin heile tarjothaan maholisuuen saaja menttorin, jonka kans puhhuut ja tehhä assiita kvääniksi Motiveerata ihmissii siihen ette oppiit kväänin kieltä ja näyttäät heile ette sillä saapi työn ja ette työtä oon nokko kaikile.",
                            element_number=0,
                        )
                    ],
                }
            ),
            AlignmentsEtc(
                {
                    0: [
                        AElement(
                            text="Forsøke selv å være gode forbilder.",
                            element_number=2,
                        )
                    ],
                    1: [
                        AElement(
                            text="Freistata itte olla hyvät esikuvat.",
                            element_number=1,
                        )
                    ],
                }
            ),
        ]
    )


def load_anchor_words():
    anchor_words = """1* / 1*, okta, ovtta
mill, million* / milj, miljovdna*, miljovnna*
Sametinget* / Sámedigg*, Sámedikk*
om / birra
"""
    anchor_word_list = alignmentmodel.AnchorWordList()
    anchor_word_list.entries = [
        AnchorWordListEntry(line.strip()) for line in anchor_words.splitlines()
    ]

    return anchor_word_list


def test_suggest3():
    trees = [
        etree.fromstring(
            """
    <document>
        <s id="1">- regjeringen.no</s>
        <s id="2">Ot.prp. nr. 25 (2006-2007)</s>
        <s id="3">Om lov om reindrift (reindriftsloven)</s>
    </document>
    """  # noqa: E501
        ),
        etree.fromstring(
            """
    <document>
        <s id="1">- regjeringen.no</s>
        <s id="2">Boazodoallolága birra</s>
    </document>
    """  # noqa: E501
        ),
    ]

    model = alignmentmodel.AlignmentModel(keys=range(2))
    model.load_trees(trees)
    model.anchor_word_list = load_anchor_words()

    model.suggets_without_gui()

    assert model.aligned == Aligned(
        [
            AlignmentsEtc(
                {
                    0: [
                        AElement(
                            text="- regjeringen.no",
                            element_number=0,
                        )
                    ],
                    1: [
                        AElement(
                            text="- regjeringen.no",
                            element_number=0,
                        )
                    ],
                }
            ),
            AlignmentsEtc(
                {
                    0: [
                        AElement(
                            text="Ot.prp. nr. 25 (2006-2007)",
                            element_number=1,
                        )
                    ]
                }
            ),
            AlignmentsEtc(
                {
                    0: [
                        AElement(
                            text="Om lov om reindrift (reindriftsloven)",
                            element_number=2,
                        )
                    ],
                    1: [
                        AElement(
                            text="Boazodoallolága birra",
                            element_number=1,
                        )
                    ],
                }
            ),
        ]
    )


def test_anchorword_hits():
    trees = [
        etree.fromstring(
            """
    <document>
        <s id="1">1 million kroner til landbruket i arktisk</s>
    </document>
    """  # noqa: E501
        ),
        etree.fromstring(
            """
    <document>
        <s id="1">1 miljon ruvnno árktalaš eanadollui</s>
    </document>
    """  # noqa: E501
        ),
    ]

    model = alignmentmodel.AlignmentModel(keys=range(2))
    model.load_trees(trees)
    model.anchor_word_list = load_anchor_words()
    model.suggets_without_gui()
    interesting = model.compare.matrix.cells["0,0,0,0"]

    found_hits = [
        [hit.to_json() for hit in lang_hits]
        for lang_hits in interesting.element_info_to_be_compared.find_hits()
    ]
    assert found_hits == [
        [
            {"index": 0, "element_number": 0, "pos": 0, "word": "1"},
            {"index": 1, "element_number": 0, "pos": 1, "word": "million"},
        ],
        [{"index": 0, "element_number": 0, "pos": 0, "word": "1"}],
    ]


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

    model = alignmentmodel.AlignmentModel(keys=range(2))
    model.load_trees(trees)
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
                            {"index": 0, "element_number": 0, "pos": 0, "word": "1"},
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
                            {"index": 0, "element_number": 2, "pos": 3, "word": "1"},
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
                            {"index": 0, "element_number": 2, "pos": 3, "word": "1"},
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
                    },
                    "best_path_score": -1.0,
                },
                "0,0,0,-1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                                        {
                                            "match_type": 0,
                                            "weight": 1.0,
                                            "t": 1,
                                            "element_number": 0,
                                            "pos": 0,
                                            "length": 1,
                                            "word": "1",
                                        },
                                        {
                                            "match_type": 0,
                                            "weight": 1.0,
                                            "t": 0,
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
                                        {
                                            "match_type": 0,
                                            "weight": 1.0,
                                            "t": 1,
                                            "element_number": 0,
                                            "pos": 0,
                                            "length": 1,
                                            "word": "1",
                                        },
                                        {
                                            "match_type": 0,
                                            "weight": 1.0,
                                            "t": 0,
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
                    },
                    "best_path_score": -1.0,
                },
                "0,0,1,0": {
                    "element_info_to_be_compared": {
                        "score": -99999.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "0,1,-1,1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                    },
                    "best_path_score": -1.0,
                },
                "0,1,0,0": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                    },
                    "best_path_score": 4.0,
                },
                "0,1,0,1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                                "length": 20,
                                "num_words": 3,
                                "words": ["27", "Geassemánnu", "2014"],
                                "anchor_word_hits": [],
                                "scoring_characters": "",
                                "proper_names": ["Geassemánnu"],
                            },
                        ],
                    },
                    "best_path_score": 4.999,
                },
                "0,1,0,2": {
                    "element_info_to_be_compared": {
                        "score": -99999.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                    "best_path_score": -1.0,
                },
                "0,1,1,1": {
                    "element_info_to_be_compared": {
                        "score": -99999.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                                "element_number": 1,
                                "length": 20,
                                "num_words": 3,
                                "words": ["27", "Geassemánnu", "2014"],
                                "anchor_word_hits": [],
                                "scoring_characters": "",
                                "proper_names": ["Geassemánnu"],
                            },
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "0,2,-1,2": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                    },
                    "best_path_score": -1.0,
                },
                "0,2,0,1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                                        {
                                            "match_type": 0,
                                            "weight": 1.0,
                                            "t": 1,
                                            "element_number": 2,
                                            "pos": 3,
                                            "length": 1,
                                            "word": "1",
                                        },
                                        {
                                            "match_type": 0,
                                            "weight": 1.0,
                                            "t": 0,
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
                                        {
                                            "match_type": 0,
                                            "weight": 1.0,
                                            "t": 1,
                                            "element_number": 2,
                                            "pos": 3,
                                            "length": 1,
                                            "word": "1",
                                        },
                                        {
                                            "match_type": 0,
                                            "weight": 1.0,
                                            "t": 0,
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
                    "best_path_score": 4.999,
                },
                "0,3,0,2": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                    },
                    "best_path_score": 4.999,
                },
                "1,0,0,0": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                    },
                    "best_path_score": 4.0,
                },
                "1,0,1,-1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                    },
                    "best_path_score": -1.0,
                },
                "1,0,1,0": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "1,0,1,1": {
                    "element_info_to_be_compared": {
                        "score": -99999.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                    },
                    "best_path_score": -1.0,
                },
                "1,0,2,0": {
                    "element_info_to_be_compared": {
                        "score": -99999.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "1,1,0,1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                    },
                    "best_path_score": 4.999,
                },
                "1,1,1,0": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                                "element_number": 1,
                                "length": 20,
                                "num_words": 3,
                                "words": ["27", "Geassemánnu", "2014"],
                                "anchor_word_hits": [],
                                "scoring_characters": "",
                                "proper_names": ["Geassemánnu"],
                            },
                        ],
                    },
                    "best_path_score": -1.0,
                },
                "1,1,1,2": {
                    "element_info_to_be_compared": {
                        "score": -99999.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                    "best_path_score": -1.0,
                },
                "1,1,2,1": {
                    "element_info_to_be_compared": {
                        "score": -99999.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                    },
                    "best_path_score": -1.0,
                },
                "1,2,0,2": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                    },
                    "best_path_score": -1.0,
                },
                "1,2,1,1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                    },
                    "best_path_score": 11.0,
                },
                "1,2,1,2": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                                        {
                                            "match_type": 0,
                                            "weight": 1.0,
                                            "t": 1,
                                            "element_number": 2,
                                            "pos": 3,
                                            "length": 1,
                                            "word": "1",
                                        },
                                        {
                                            "match_type": 0,
                                            "weight": 1.0,
                                            "t": 0,
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
                    "best_path_score": -1.0,
                },
                "1,3,1,2": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                    },
                    "best_path_score": 11.0,
                },
                "2,0,1,0": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                    },
                    "best_path_score": 4.0,
                },
                "2,0,2,-1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                                        {
                                            "match_type": 0,
                                            "weight": 1.0,
                                            "t": 1,
                                            "element_number": 0,
                                            "pos": 0,
                                            "length": 1,
                                            "word": "1",
                                        },
                                        {
                                            "match_type": 0,
                                            "weight": 1.0,
                                            "t": 0,
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
                                        {
                                            "match_type": 0,
                                            "weight": 1.0,
                                            "t": 1,
                                            "element_number": 0,
                                            "pos": 0,
                                            "length": 1,
                                            "word": "1",
                                        },
                                        {
                                            "match_type": 0,
                                            "weight": 1.0,
                                            "t": 0,
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
                    },
                    "best_path_score": -1.0,
                },
                "2,1,1,1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                    },
                    "best_path_score": 11.0,
                },
                "2,1,2,0": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                    },
                    "best_path_score": 3.0,
                },
                "2,1,2,1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                                        {
                                            "match_type": 0,
                                            "weight": 1.0,
                                            "t": 1,
                                            "element_number": 2,
                                            "pos": 3,
                                            "length": 1,
                                            "word": "1",
                                        },
                                        {
                                            "match_type": 0,
                                            "weight": 1.0,
                                            "t": 0,
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
                    "best_path_score": 8.998,
                },
                "2,2,1,2": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                    },
                    "best_path_score": 4.999,
                },
                "2,2,2,1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                                        {
                                            "match_type": 0,
                                            "weight": 1.0,
                                            "t": 1,
                                            "element_number": 2,
                                            "pos": 3,
                                            "length": 1,
                                            "word": "1",
                                        },
                                        {
                                            "match_type": 0,
                                            "weight": 1.0,
                                            "t": 0,
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
                    "best_path_score": 8.998999999999999,
                },
                "2,3,2,2": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                    },
                    "best_path_score": 16.0,
                },
                "3,0,2,0": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                    },
                    "best_path_score": 4.0,
                },
                "3,1,2,1": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
                    },
                    "best_path_score": 11.0,
                },
                "3,2,2,2": {
                    "element_info_to_be_compared": {
                        "score": 0.0,
                        "common_clusters": {"clusters": []},
                        "info": [
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
