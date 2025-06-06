from dataclasses import asdict

from python_tca2 import alignmentmodel
from python_tca2.aelement import AlignmentElement
from python_tca2.aligned import Aligned
from python_tca2.aligned_sentence_elements import (
    AlignedSentenceElements,
    to_string_tuple,
)
from python_tca2.anchorwordlist import AnchorWordList
from python_tca2.anchorwordlistentry import AnchorWordListEntry
from python_tca2.elementinfotobecompared import ElementInfoToBeCompared


def test_get_score():
    """Test that the first if in find_dice_matches works as expected"""
    expected_score = 4.0
    eitbc = ElementInfoToBeCompared(
        (
            [
                AlignmentElement(
                    anchor_word_list=AnchorWordList(),
                    text="Mobil",
                    text_number=0,
                    element_number=0,
                )
            ],
            [
                AlignmentElement(
                    anchor_word_list=AnchorWordList(),
                    text="Mobiila",
                    text_number=1,
                    element_number=0,
                )
            ],
        )
    )

    assert eitbc.get_score() == expected_score


def test_alignment_etcs():
    aligned_sentence_elements = AlignedSentenceElements(
        (
            [
                AlignmentElement(
                    anchor_word_list=AnchorWordList(),
                    text="element0",
                    text_number=0,
                    element_number=0,
                ),
                AlignmentElement(
                    anchor_word_list=AnchorWordList(),
                    text="element1",
                    text_number=0,
                    element_number=1,
                ),
            ],
            [
                AlignmentElement(
                    anchor_word_list=AnchorWordList(),
                    text="element2",
                    text_number=1,
                    element_number=0,
                ),
                AlignmentElement(
                    anchor_word_list=AnchorWordList(),
                    text="element3",
                    text_number=1,
                    element_number=1,
                ),
                AlignmentElement(
                    anchor_word_list=AnchorWordList(),
                    text="element4",
                    text_number=1,
                    element_number=2,
                ),
            ],
        )
    )
    assert to_string_tuple(aligned_sentence_elements) == (
        "element0 element1",
        "element2 element3 element4",
    )


def test_find_dice_matches():
    """Test that the first if in find_dice_matches works as expected"""
    eitbc = ElementInfoToBeCompared(
        (
            [
                AlignmentElement(
                    anchor_word_list=AnchorWordList(),
                    text="Mobil",
                    text_number=0,
                    element_number=0,
                )
            ],
            [
                AlignmentElement(
                    anchor_word_list=AnchorWordList(),
                    text="Mobiila",
                    text_number=1,
                    element_number=0,
                )
            ],
        )
    )

    eitbc.find_dice_matches()

    assert eitbc.to_json() == {
        "score": 4.0,
        "info": [
            {
                "element_number": 0,
                "length": 5,
                "num_words": 1,
                "text_number": 0,
                "text": "Mobil",
                "words": ["Mobil"],
                "anchor_word_hits": {"hits": []},
                "scoring_characters": "",
            },
            {
                "element_number": 0,
                "length": 7,
                "num_words": 1,
                "text": "Mobiila",
                "text_number": 1,
                "words": ["Mobiila"],
                "anchor_word_hits": {"hits": []},
                "scoring_characters": "",
            },
        ],
    }


def test_aelement_text():
    """Check that space is normalised in aelement.element"""
    sentence = "9 Økonomiske, administrative og miljømessige konsekvenser"

    aelement = AlignmentElement(
        anchor_word_list=AnchorWordList(),
        text=sentence,
        text_number=0,
        element_number=0,
    )

    assert aelement.text == "9 Økonomiske, administrative og miljømessige konsekvenser"


def test_aligned_to_text_file():
    aligned = Aligned([])
    a1 = AlignedSentenceElements(
        (
            [],
            [
                AlignmentElement(
                    anchor_word_list=AnchorWordList(),
                    text="Oslon tjïelte ( Oslon geažus -n ea genetiivageažus) .",
                    text_number=1,
                    element_number=13,
                ),
            ],
        )
    )
    a2 = AlignedSentenceElements(
        (
            [
                AlignmentElement(
                    anchor_word_list=AnchorWordList(),
                    text="Aldri noensinne har språkuka og samiske språk fått så mye oppmerksomhet i samfunnet.",  # noqa: E501
                    text_number=0,
                    element_number=5,
                )
            ],
            [
                AlignmentElement(
                    anchor_word_list=AnchorWordList(),
                    text="Sámi giellavahkku",
                    text_number=1,
                    element_number=14,
                ),
                AlignmentElement(
                    anchor_word_list=AnchorWordList(),
                    text="Ii goassege leat Giellavahkku ja sámegielat ná bures fuomášuvvon servodagas.",  # noqa: E501
                    text_number=1,
                    element_number=15,
                ),
            ],
        )
    )
    aligned.alignments = [
        a1,
        a2,
    ]
    assert aligned.non_empty_pairs() == [
        (
            "Aldri noensinne har språkuka og samiske språk fått så mye oppmerksomhet i samfunnet.",  # noqa: E501
            "Sámi giellavahkku Ii goassege leat Giellavahkku ja sámegielat ná bures fuomášuvvon servodagas.",  # noqa: E501
        ),
    ]


# A simple test of the alignment model
def test_suggest1():
    strings = [
        """Kanskje en innkjøpsordning for kvenskspråklig litteratur.
Utvikling av undervisnings- og lærematerialer.
""",
        """Kvääninkielinen litteratuuri osto-oorninkhiin piian.
Opetus- ja oppimateriaaliitten kehittäminen.
""",
    ]

    model = alignmentmodel.AlignmentModel(
        sentences_tuple=(strings[0].splitlines(), strings[1].splitlines()),
        anchor_word_list=load_anchor_words(),
    )
    aligned = model.suggest_without_gui()

    assert aligned.non_empty_pairs() == [
        (
            "Kanskje en innkjøpsordning for kvenskspråklig litteratur.",
            "Kvääninkielinen litteratuuri osto-oorninkhiin piian.",
        ),
        (
            "Utvikling av undervisnings- og lærematerialer.",
            "Opetus- ja oppimateriaaliitten kehittäminen.",
        ),
    ]


# A test of the alignment model, with different number of sentences
def test_suggest2():
    strings = [
        """Når folk har gått på nybegynnerkursene hos enten instituttet eller universitetet, kan man tilby dem muligheten å få en mentor som de kan snakke kvensk med og gjøre aktiviteter med på kvensk.
Motivere folk til å lære kvensk og vise dem at man får jobb med det, og at det er nok arbeid til alle.
Forsøke selv å være gode forbilder.
""",  # noqa: E501
        """Ko ihmiset oon käynheet institutin tahi universiteetin alkukurssin, niin heile tarjothaan maholisuuen saaja menttorin, jonka kans puhhuut ja tehhä assiita kvääniksi Motiveerata ihmissii siihen ette oppiit kväänin kieltä ja näyttäät heile ette sillä saapi työn ja ette työtä oon nokko kaikile.
Freistata itte olla hyvät esikuvat.
""",  # noqa: E501
    ]

    model = alignmentmodel.AlignmentModel(
        sentences_tuple=(strings[0].splitlines(), strings[1].splitlines()),
        anchor_word_list=load_anchor_words(),
    )
    aligned = model.suggest_without_gui()

    assert aligned.non_empty_pairs() == [
        (
            "Når folk har gått på nybegynnerkursene hos enten instituttet eller "
            "universitetet, kan man tilby dem muligheten å få en mentor som de kan "
            "snakke kvensk med og gjøre aktiviteter med på kvensk. Motivere folk "
            "til å lære kvensk og vise dem at man får jobb med det, og at det er "
            "nok arbeid til alle.",
            "Ko ihmiset oon käynheet institutin tahi universiteetin alkukurssin, "
            "niin heile tarjothaan maholisuuen saaja menttorin, jonka kans puhhuut "
            "ja tehhä assiita kvääniksi Motiveerata ihmissii siihen ette oppiit "
            "kväänin kieltä ja näyttäät heile ette sillä saapi työn ja ette työtä "
            "oon nokko kaikile.",
        ),
        (
            "Forsøke selv å være gode forbilder.",
            "Freistata itte olla hyvät esikuvat.",
        ),
    ]


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
    strings = [
        """- regjeringen.no
Ot.prp. nr. 25 (2006-2007)
Om lov om reindrift (reindriftsloven)
""",
        """- regjeringen.no
Boazodoallolága birra
""",
    ]

    model = alignmentmodel.AlignmentModel(
        sentences_tuple=(strings[0].splitlines(), strings[1].splitlines()),
        anchor_word_list=load_anchor_words(),
    )
    aligned = model.suggest_without_gui()

    assert aligned.non_empty_pairs() == [
        (
            "- regjeringen.no",
            "- regjeringen.no",
        ),
        (
            "Om lov om reindrift (reindriftsloven)",
            "Boazodoallolága birra",
        ),
    ]


def test_anchorword_hits():
    strings = [
        "1 million kroner til landbruket i arktisk",
        "1 miljon ruvnno árktalaš eanadollui",
    ]

    model = alignmentmodel.AlignmentModel(
        sentences_tuple=(strings[0].splitlines(), strings[1].splitlines()),
        anchor_word_list=load_anchor_words(),
    )
    interesting = ElementInfoToBeCompared(
        aligned_sentence_elements=model.get_aligned_sentence_elements(
            slices=(
                slice(0, 1),
                slice(0, 1),
            ),
        )
    )

    found_hits = [
        [asdict(hit) for hit in lang_hits] for lang_hits in interesting.find_hits()
    ]
    assert found_hits == [
        [
            {"index": 0, "element_number": 0, "pos": 0, "word": "1"},
            {"index": 1, "element_number": 0, "pos": 1, "word": "million"},
        ],
        [{"index": 0, "element_number": 0, "pos": 0, "word": "1"}],
    ]
