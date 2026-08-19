from dataclasses import asdict
from pathlib import Path

import pytest
from lxml import etree

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
from python_tca2.tmx import write_streaming_result


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
    sentence = "9 Økonomiske,  administrative og miljømessige konsekvenser"

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


def test_streaming_alignment_uses_bounded_input_window():
    line_count = 100
    sentences = tuple(
        "\n".join(f"Sentence {index}" for index in range(line_count))
        for _ in range(2)
    )
    model = alignmentmodel.AlignmentModel(
        sentences_tuple=tuple(
            iter(sentence.splitlines()) for sentence in sentences
        ),
        anchor_word_list=AnchorWordList(),
    )

    aligned_pairs = [
        to_string_tuple(alignment) for alignment in model.iter_alignment_elements()
    ]

    assert aligned_pairs == [
        (f"Sentence {index}", f"Sentence {index}") for index in range(line_count)
    ]
    assert model.max_buffer_size <= (
        2 * alignmentmodel.constants.MAX_PATH_LENGTH * 2
    )


def test_alignment_model_has_a_search():
    model = alignmentmodel.AlignmentModel(
        sentences_tuple=(iter(["First"]), iter(["Second"])),
        anchor_word_list=AnchorWordList(),
    )

    assert isinstance(model.search, alignmentmodel.AlignmentSearch)
    assert not isinstance(model, alignmentmodel.AlignmentSearch)


def test_write_streaming_result_writes_tmx_and_html(tmp_path):
    alignment = AlignedSentenceElements(
        (
            [
                AlignmentElement(
                    anchor_word_list=AnchorWordList(),
                    text="First & sentence",
                    text_number=0,
                    element_number=0,
                )
            ],
            [
                AlignmentElement(
                    anchor_word_list=AnchorWordList(),
                    text="Second sentence",
                    text_number=1,
                    element_number=0,
                )
            ],
        )
    )
    file_path = tmp_path / "first.txt"

    write_streaming_result(
        file1_path=file_path,
        language_pair=("nob", "sme"),
        alignments=iter([alignment]),
        output_format="tmx",
    )
    write_streaming_result(
        file1_path=file_path,
        language_pair=("nob", "sme"),
        alignments=iter([alignment]),
        output_format="html",
    )

    tmx = etree.parse(tmp_path / "first.tmx")
    assert tmx.xpath("//seg/text()") == ["First & sentence", "Second sentence"]
    assert "&amp;" in (tmp_path / "first.html").read_text(encoding="utf-8")


def load_anchor_words(lang_pair: str) -> AnchorWordList:
    anchor_words = Path("tests", f"anchor-{lang_pair}.txt").read_text(encoding="utf-8")
    anchor_word_list = alignmentmodel.AnchorWordList()
    anchor_word_list.entries = [
        AnchorWordListEntry(line.strip()) for line in anchor_words.splitlines()
    ]

    return anchor_word_list


@pytest.mark.parametrize(
    ("test_name", "lang_pair", "input_strings", "expected_pairs"),
    [
        (
            "simple_alignment",
            "nob-sme",
            [
                """Kanskje en innkjøpsordning for kvenskspråklig litteratur.
Utvikling av undervisnings- og lærematerialer.
""",
                """Kvääninkielinen litteratuuri osto-oorninkhiin piian.
Opetus- ja oppimateriaaliitten kehittäminen.
""",
            ],
            [
                (
                    "Kanskje en innkjøpsordning for kvenskspråklig litteratur.",
                    "Kvääninkielinen litteratuuri osto-oorninkhiin piian.",
                ),
                (
                    "Utvikling av undervisnings- og lærematerialer.",
                    "Opetus- ja oppimateriaaliitten kehittäminen.",
                ),
            ],
        ),
        (
            "different_sentence_count",
            "nob-sme",
            [
                """Når folk har gått på nybegynnerkursene hos enten instituttet eller universitetet, kan man tilby dem muligheten å få en mentor som de kan snakke kvensk med og gjøre aktiviteter med på kvensk.
Motivere folk til å lære kvensk og vise dem at man får jobb med det, og at det er nok arbeid til alle.
Forsøke selv å være gode forbilder.
""",  # noqa: E501
                """Ko ihmiset oon käynheet institutin tahi universiteetin alkukurssin, niin heile tarjothaan maholisuuen saaja menttorin, jonka kans puhhuut ja tehhä assiita kvääniksi Motiveerata ihmissii siihen ette oppiit kväänin kieltä ja näyttäät heile ette sillä saapi työn ja ette työtä oon nokko kaikile.
Freistata itte olla hyvät esikuvat.
""",  # noqa: E501
            ],
            [
                (
                    "Når folk har gått på nybegynnerkursene hos enten "
                    "instituttet eller universitetet, kan man tilby dem "
                    "muligheten å få en mentor som de kan snakke kvensk med "
                    "og gjøre aktiviteter med på kvensk. Motivere folk til "
                    "å lære kvensk og vise dem at man får jobb med det, og "
                    "at det er nok arbeid til alle.",
                    "Ko ihmiset oon käynheet institutin tahi universiteetin "
                    "alkukurssin, niin heile tarjothaan maholisuuen saaja "
                    "menttorin, jonka kans puhhuut ja tehhä assiita kvääniksi "
                    "Motiveerata ihmissii siihen ette oppiit kväänin kieltä "
                    "ja näyttäät heile ette sillä saapi työn ja ette työtä "
                    "oon nokko kaikile.",
                ),
                (
                    "Forsøke selv å være gode forbilder.",
                    "Freistata itte olla hyvät esikuvat.",
                ),
            ],
        ),
        (
            "government_document",
            "nob-sme",
            [
                """- regjeringen.no
Ot.prp. nr. 25 (2006-2007)
Om lov om reindrift (reindriftsloven)
""",
                """- regjeringen.no
Boazodoallolága birra
""",
            ],
            [
                (
                    "- regjeringen.no",
                    "- regjeringen.no",
                ),
                (
                    "Ot.prp. nr. 25 (2006-2007)",
                    "",
                ),
                (
                    "Om lov om reindrift (reindriftsloven)",
                    "Boazodoallolága birra",
                ),
            ],
        ),
        (
            "government_document_without_first_sentence",
            "nob-sme",
            [
                """Tilråding - regjeringen.no
St.meld. nr. 55 (2000-2001)
Om samepolitikken
Tilråding
Kommunal- og regionaldepartementet
tilrår:
Tilråding fra Kommunal- og regionaldepartementet av 31. august 2001 om samepolitikken blir sendt Stortinget.
""",
                """St.dieđ. nr. 55 (2000-2001)
Sámepolitihka birra
Ráva
Gielda- ja guovlodepartemeanta
ráđđe:
Gielda- ja guovlodepartemeantta neavva addojuvvon borgemánu 31. 2001 sámepolitihka birra sáddejuvvo Stuorradiggái.
""",
            ],
            [
                ("Tilråding - regjeringen.no", ""),
                ("St.meld. nr. 55 (2000-2001)", "St.dieđ. nr. 55 (2000-2001)"),
                ("Om samepolitikken", "Sámepolitihka birra"),
                ("Tilråding", "Ráva"),
                (
                    "Kommunal- og regionaldepartementet",
                    "Gielda- ja guovlodepartemeanta",
                ),
                ("tilrår:", "ráđđe:"),
                (
                    "Tilråding fra Kommunal- og regionaldepartementet av 31. august 2001 om samepolitikken blir sendt Stortinget.",
                    "Gielda- ja guovlodepartemeantta neavva addojuvvon borgemánu 31. 2001 sámepolitihka birra sáddejuvvo Stuorradiggái.",
                ),
            ],
        ),
        (
            "big_sentence_diff",
            "nob-sme",
            [
                """Møte med Tana kommune
Sametinget avholdt et digitalt møte med Tana kommune 5.november 2021.
Møte var om at Tana kommune har behov for et mye større tospråklighetstilskudd enn det de bevilges av Sametinget.
Sametingsrådene Mikkel Eskil Mikkelsen og Runar Myrnes Balto var med på møtet.
Samisk språkuke
Aldri noensinne har språkuka og samiske språk fått så mye oppmerksomhet i samfunnet.
Sametinget så i fjor i forbindelse med pandemien at vi rekker ut til folk med filmer.
Derfor bestilte Sametinget 11 filmer til språkuka.
Sametinget har brukt mye ressurser på å synliggjøre språkuka via sosiale media.
Vi ser at det er med en bredere synliggjøring av språkuka.
Helhetlig ser Sametinget at det Norske samfunnet er klare til å gjøre mer i forbindelse med språkuka så lenge Sametinget har ressurser til å veilede og hjelpe.
Sametinget har også muligheter til å samarbeide med større aktører, hvis de begynner å planlegge i god tid.
""",
                """Čoahkkin Deanu gielddain
Sámediggi doalai digitála čoahkkima Deanu gielddain skábmamánu 5. beaivvi 2021.
Čoahkkin lei Deanu gieldda guovttegielatvuođadoarjaga dárbbuid birra mat leat olu eambbo go doarjja maid Sámediggi juolluda.
Sámediggeráđit Mikkel Eskil Mikkelsen ja Runar Myrnes Balto searvvaiga čoahkkimii.
(  FUOM!
ii dárbbaš jorgalit dan mii lea ruoksadin  , teaksta lei čállojuvvon guovtti gillii, bijan dušše dása vai ii láhppo  )
Sámi báikenammanevvohat
Báikenammanevvohat lea sádden álgorávvemiid Gáivuonas, Sáččás ja  Ulbbis  , ja loahpalaš rávvemiid Mátta-Várjjagis, Loabágis ja Rørosas.
Sámediggi lea maid dán áigodagas sádden ođđa vástádusa Oslo suohkana jearaldahkii, mas bivde sámegiel nama Oslo gávpogii.
Duogážin dán áššis lea ahte nammanevvohaga vuosttaš rávvema geažil šattai dát mediaáššin, ja nammanevvohat válljii guorahallat ášši ođđasit.
Nammanevvohat lea dál čađahan ođđa nammafágalaš guorahallama, ja boađusin lea ahte nammanevvohat doalaha ovddit rávvema, namalassii ahte Oslo bisuhuvvo hámis Oslo.
Nammanevvohat árvala reivvestis ahte Oslo suohkan váldá atnui sámegiel nama suohkanii čuovvovaččat:  dsg  .
Oslo suohkan  /  gielda  ~ jsg.  Oslo suohkan  ~ lsg.
Oslon  tjïelte  (  Oslon  geažus -n ea genetiivageažus)  .
Sámi giellavahkku
Ii goassege leat Giellavahkku ja sámegielat ná bures fuomášuvvon servodagas.
Sámediggi oinnii diibmá pandemiija oktavuođas ahte olahit olbmuide filmmaiguin.
Dan dihte diŋgui Sámediggi 11 filmma Giellavahkkui.
Sámediggi lea atnán ollu resurssaid čalmmustahttit Giellavahku sosiála mediaid bokte.
Mii oaidnit ahte dat lea mielde čalmmustahttime Giellavahku viidát.
Ollislaččat oaidná Sámediggi ahte Norgga servodat lea gearggus dahkat eanet Giellavahku oktavuođas nu guhká go Sámedikkis leat resurssat sin láidestit ja veahkehit.
Sámedikkis lea maid vejolašvuohta oažžut ovttasbarggu stuorit aktevrraiguin, jus buori áiggis oččodišgoahtit ovttasbarggu.
""",
            ],
            [
                ("Møte med Tana kommune", "Čoahkkin Deanu gielddain"),
                (
                    "Sametinget avholdt et digitalt møte med Tana kommune 5.november 2021.",
                    "Sámediggi doalai digitála čoahkkima Deanu gielddain skábmamánu 5. beaivvi 2021.",
                ),
                (
                    "Møte var om at Tana kommune har behov for et mye større tospråklighetstilskudd enn det de bevilges av Sametinget.",
                    "Čoahkkin lei Deanu gieldda guovttegielatvuođadoarjaga dárbbuid birra mat leat olu eambbo go doarjja maid Sámediggi juolluda.",
                ),
                (
                    "Sametingsrådene Mikkel Eskil Mikkelsen og Runar Myrnes Balto var med på møtet.",
                    "Sámediggeráđit Mikkel Eskil Mikkelsen ja Runar Myrnes Balto searvvaiga čoahkkimii.",
                ),
                ("", "( FUOM!"),
                (
                    "",
                    "ii dárbbaš jorgalit dan mii lea ruoksadin , teaksta lei čállojuvvon guovtti gillii, bijan dušše dása vai ii láhppo )",
                ),
                ("Samisk språkuke", "Sámi báikenammanevvohat"),
                (
                    "",
                    "Báikenammanevvohat lea sádden álgorávvemiid Gáivuonas, Sáččás ja Ulbbis , ja loahpalaš rávvemiid Mátta-Várjjagis, Loabágis ja Rørosas.",
                ),
                (
                    "",
                    "Sámediggi lea maid dán áigodagas sádden ođđa vástádusa Oslo suohkana jearaldahkii, mas bivde sámegiel nama Oslo gávpogii.",
                ),
                (
                    "",
                    "Duogážin dán áššis lea ahte nammanevvohaga vuosttaš rávvema geažil šattai dát mediaáššin, ja nammanevvohat válljii guorahallat ášši ođđasit.",
                ),
                (
                    "",
                    "Nammanevvohat lea dál čađahan ođđa nammafágalaš guorahallama, ja boađusin lea ahte nammanevvohat doalaha ovddit rávvema, namalassii ahte Oslo bisuhuvvo hámis Oslo.",
                ),
                (
                    "",
                    "Nammanevvohat árvala reivvestis ahte Oslo suohkan váldá atnui sámegiel nama suohkanii čuovvovaččat: dsg .",
                ),
                ("", "Oslo suohkan / gielda ~ jsg. Oslo suohkan ~ lsg."),
                ("", "Oslon tjïelte ( Oslon geažus -n ea genetiivageažus) ."),
                (
                    "Aldri noensinne har språkuka og samiske språk fått så mye oppmerksomhet i samfunnet.",
                    "Sámi giellavahkku Ii goassege leat Giellavahkku ja sámegielat ná bures fuomášuvvon servodagas.",
                ),
                (
                    "Sametinget så i fjor i forbindelse med pandemien at vi rekker ut til folk med filmer.",
                    "Sámediggi oinnii diibmá pandemiija oktavuođas ahte olahit olbmuide filmmaiguin.",
                ),
                (
                    "Derfor bestilte Sametinget 11 filmer til språkuka.",
                    "Dan dihte diŋgui Sámediggi 11 filmma Giellavahkkui.",
                ),
                (
                    "Sametinget har brukt mye ressurser på å synliggjøre språkuka via sosiale media.",
                    "Sámediggi lea atnán ollu resurssaid čalmmustahttit Giellavahku sosiála mediaid bokte.",
                ),
                (
                    "Vi ser at det er med en bredere synliggjøring av språkuka.",
                    "Mii oaidnit ahte dat lea mielde čalmmustahttime Giellavahku viidát.",
                ),
                (
                    "Helhetlig ser Sametinget at det Norske samfunnet er klare til å gjøre mer i forbindelse med språkuka så lenge Sametinget har ressurser til å veilede og hjelpe.",
                    "Ollislaččat oaidná Sámediggi ahte Norgga servodat lea gearggus dahkat eanet Giellavahku oktavuođas nu guhká go Sámedikkis leat resurssat sin láidestit ja veahkehit.",
                ),
                (
                    "Sametinget har også muligheter til å samarbeide med større aktører, hvis de begynner å planlegge i god tid.",
                    "Sámedikkis lea maid vejolašvuohta oažžut ovttasbarggu stuorit aktevrraiguin, jus buori áiggis oččodišgoahtit ovttasbarggu.",
                ),
            ],
        ),
        (
            "nob_concat",
            "nob-sme",
            [
                """Fremmedspråk og norsk sidemål skriftlig – ikke obligatorisk
Elever som har samisk som første- eller andrespråk, er fritatt i norsk sidemål skriftlig og i faget fremmedspråk.
Elever med samisk som førstespråk eller andrespråk, er fritatt for opplæring og vurdering i norsk sidemål både på grunnskole og videregående opplæring, jf.Opplæringslova § 1-11.
Fremmedspråk (eller språkfordypning eller arbeidslivsfag) er obligatorisk fag for alle unntatt for elever som har samisk som første- eller andrespråk på skolen.
Disse har tre språkfag;
samisk, norsk og engelsk, og de er fritatt fra dette både på grunnskolen og videregående opplæring, men de har likevel rett til å ha fremmedspråk dersom de ønsker det, jf. Forskrift til opplæringslova § 1-9 og 1-10.
For å unngå mye ekstratimer for disse elevene, er det en bestemmelse for grunnskolen om at elever som velger fremmedspråk i tillegg til samisk, kan ha lavere minstetimetall i fremmedspråk på grunnskolen enn det som er det ordinære kravet for faget.
Dersom en elev ønsker å ha fremmedspråk som fag på videregående, uten å ha hatt faget i grunnskolen, blir det godkjent at de fullfører nivå 1 på bare ett fremmedspråk på videregående opplæring.
Elever uten samisk, skal fullføre nivå 1 og 2 i ett fremmedspråk, eller fullføre nivå 1 i to ulike fremmedspråk
Mere opplysninger om organisering og timetall finner du på Utdanningsdirektoratets nettsider i Rundskriv om fag- og timefordeling.
NB!
Denne fornyes hvert år.
""",
                """Vierisgiella ja dárogiella siidogiella ii leat bákkolaš
Oahppit geain lea sámegiella vuosttaš- dahje nubbingiellan, leat luvvejuvvon čálalaš dárogiella siidogielas ja vierisgiellafágas.
Oahppit geain lea fága sámegiella vuosttašgiellan dahje sámegiella nubbingiellan, leat luvvejuvvon dárogiella siidogiella oahpahusas ja árvvoštallamis, gč. Oahpahusláhka § 1-11.
Vierisgiella (dahje giellačiekŋudeapmi dahje bargoeallinfága) lea bákkolaš fága buohkaide earret ohppiide geain lea sámegiella vuosttaš- dahje nubbingiellan skuvllas.
Sis leat golbma giellafága;
sámegiella, dárogiella ja eŋgelasgiella, ja sii leat luvvejuvvon vierisgiellaoahpahusas sihke vuođđoskuvllas ja joatkkaoahpahusas, muhto sis lea vuoigatvuohta oažžut oahpu vierisgielas jus háliidit, gč. Oahpahuslága láhkaásahus §1-9 ja 1-10.
Garvin dihte ahte dát oahppit šaddet váldit ollu liigediimmuid, de lea vuođđoskuvllas sierra njuolggadus ahte sáhttá leat unnit diibmolohku vierisgielas go dat dábálaš gáibádus fágas.
Jus oahppit geain lea sámegiella vuosttaš- dahje nubbingiellan, háliidit vierisgiela fágan joatkkaoahpahusas, vaikko ii leat leamašan dát fága vuođđoskuvllas, de dohkkehuvvo ahte sii čađahit ovtta vierisgielas dási 1. Oahppit geain ii leat sámegiella, galget čađahit ovtta gielas dásiid 1 ja 2 dahje guovtti gielas dási 1.
Eanet dieđuid organiserema ja diibmologuid birra gávnnat Utdanningsdirektoráhta neahttabáikkis čállosis: Rundskriv om fag- og timefordeling.
Mearkkaš ahte dat ođastuvvo juohke jagi.
""",
            ],
            [
                (
                    "Fremmedspråk og norsk sidemål skriftlig – ikke obligatorisk",
                    "Vierisgiella ja dárogiella siidogiella ii leat bákkolaš",
                ),
                (
                    "Elever som har samisk som første- eller andrespråk, er fritatt i norsk sidemål skriftlig og i faget fremmedspråk.",
                    "Oahppit geain lea sámegiella vuosttaš- dahje nubbingiellan, leat luvvejuvvon čálalaš dárogiella siidogielas ja vierisgiellafágas.",
                ),
                (
                    "Elever med samisk som førstespråk eller andrespråk, er fritatt for opplæring og vurdering i norsk sidemål både på grunnskole og videregående opplæring, jf.Opplæringslova § 1-11.",
                    "Oahppit geain lea fága sámegiella vuosttašgiellan dahje sámegiella nubbingiellan, leat luvvejuvvon dárogiella siidogiella oahpahusas ja árvvoštallamis, gč. Oahpahusláhka § 1-11.",
                ),
                (
                    "Fremmedspråk (eller språkfordypning eller arbeidslivsfag) er obligatorisk fag for alle unntatt for elever som har samisk som første- eller andrespråk på skolen.",
                    "Vierisgiella (dahje giellačiekŋudeapmi dahje bargoeallinfága) lea bákkolaš fága buohkaide earret ohppiide geain lea sámegiella vuosttaš- dahje nubbingiellan skuvllas.",
                ),
                ("Disse har tre språkfag;", "Sis leat golbma giellafága;"),
                (
                    "samisk, norsk og engelsk, og de er fritatt fra dette både på grunnskolen og videregående opplæring, men de har likevel rett til å ha fremmedspråk dersom de ønsker det, jf. Forskrift til opplæringslova § 1-9 og 1-10.",
                    "sámegiella, dárogiella ja eŋgelasgiella, ja sii leat luvvejuvvon vierisgiellaoahpahusas sihke vuođđoskuvllas ja joatkkaoahpahusas, muhto sis lea vuoigatvuohta oažžut oahpu vierisgielas jus háliidit, gč. Oahpahuslága láhkaásahus §1-9 ja 1-10.",
                ),
                (
                    "For å unngå mye ekstratimer for disse elevene, er det en bestemmelse for grunnskolen om at elever som velger fremmedspråk i tillegg til samisk, kan ha lavere minstetimetall i fremmedspråk på grunnskolen enn det som er det ordinære kravet for faget.",
                    "Garvin dihte ahte dát oahppit šaddet váldit ollu liigediimmuid, de lea vuođđoskuvllas sierra njuolggadus ahte sáhttá leat unnit diibmolohku vierisgielas go dat dábálaš gáibádus fágas.",
                ),
                (
                    "Dersom en elev ønsker å ha fremmedspråk som fag på videregående, uten å ha hatt faget i grunnskolen, blir det godkjent at de fullfører nivå 1 på bare ett fremmedspråk på videregående opplæring. Elever uten samisk, skal fullføre nivå 1 og 2 i ett fremmedspråk, eller fullføre nivå 1 i to ulike fremmedspråk",
                    "Jus oahppit geain lea sámegiella vuosttaš- dahje nubbingiellan, háliidit vierisgiela fágan joatkkaoahpahusas, vaikko ii leat leamašan dát fága vuođđoskuvllas, de dohkkehuvvo ahte sii čađahit ovtta vierisgielas dási 1. Oahppit geain ii leat sámegiella, galget čađahit ovtta gielas dásiid 1 ja 2 dahje guovtti gielas dási 1.",
                ),
                (
                    "Mere opplysninger om organisering og timetall finner du på Utdanningsdirektoratets nettsider i Rundskriv om fag- og timefordeling.",
                    "Eanet dieđuid organiserema ja diibmologuid birra gávnnat Utdanningsdirektoráhta neahttabáikkis čállosis: Rundskriv om fag- og timefordeling.",
                ),
                ("NB!", ""),
                ("Denne fornyes hvert år.", "Mearkkaš ahte dat ođastuvvo juohke jagi."),
            ],
        ),
    ],
)
def test_suggest(
    test_name: str,
    lang_pair: str,
    input_strings: list[str],
    expected_pairs: list[tuple[str, str]],
):
    """Test the alignment model with various input configurations."""
    model = alignmentmodel.AlignmentModel(
        sentences_tuple=(input_strings[0].splitlines(), input_strings[1].splitlines()),
        anchor_word_list=load_anchor_words(lang_pair),
    )
    aligned_pairs = [
        to_string_tuple(alignment) for alignment in model.iter_alignment_elements()
    ]

    assert aligned_pairs == expected_pairs, f"Test '{test_name}' failed"


@pytest.mark.skip(reason="Must find a more stable way to compute scores")
def test_suggest_fail():
    """Floating point numbers behave differently in python and java.

    The example below shows an example of different behavior in python and java
    triggered by the content of this test.

    Python:
        Does 1,2 have it: step={1,1}
        score before adjustment 7.25
        score after adjustment 8.25
        score 3.999 + stepScore 8.25 = 12.249
        score 3999000000.0 + stepScore 8250000000.0 = 12249000000.0
        Not adding: 12.249 <= 12.249 for [1, 2]

    Java:
        Does 1,2 have it: step={1,1}
        score before adjustment 7.25
        score after adjustment 8.25
        score + 3.999 stepScore =  8.25 = 12.249001
        score + 3999000064 stepScore =  8249999872 = 12248999936
    1,2 has it -> 12.249001
    """
    test_name = "second_sentence_moves_compared_to_java"
    lang_pair = "sme-nob"
    input_strings = [
        """Vel eanet borramuš!
Juovllat lea borramuš áigi, muhto giđđat maid šaddá sáhka borramuša birra.""",
        """Enda mer mat... 
til våren
Julen er tid for mat, men også til våren blir det mye mat.""",
    ]
    expected_pairs = [
        (
            "Vel eanet borramuš!",
            "Enda mer mat... til våren",
        ),
        (
            "Juovllat lea borramuš áigi, muhto giđđat maid šaddá sáhka borramuša birra.",
            "Julen er tid for mat, men også til våren blir det mye mat.",
        ),
    ]
    model = alignmentmodel.AlignmentModel(
        sentences_tuple=(input_strings[0].splitlines(), input_strings[1].splitlines()),
        anchor_word_list=load_anchor_words(lang_pair),
    )
    aligned_pairs = [
        to_string_tuple(alignment) for alignment in model.iter_alignment_elements()
    ]

    assert aligned_pairs == expected_pairs, f"Test '{test_name}' failed"


def test_anchorword_hits():
    strings = [
        "1 million kroner til landbruket i arktisk",
        "1 miljon ruvnno árktalaš eanadollui",
    ]

    model = alignmentmodel.AlignmentModel(
        sentences_tuple=(strings[0].splitlines(), strings[1].splitlines()),
        anchor_word_list=load_anchor_words("nob-sme"),
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
            {"index": 3, "element_number": 0, "pos": 0, "word": "1"},
            {"index": 312, "element_number": 0, "pos": 4, "word": "landbruket"},
            {"index": 581, "element_number": 0, "pos": 2, "word": "kroner"},
            {"index": 646, "element_number": 0, "pos": 1, "word": "million"},
            {"index": 1038, "element_number": 0, "pos": 3, "word": "til"},
            {"index": 1351, "element_number": 0, "pos": 6, "word": "arktisk"},
        ],
        [
            {"index": 3, "element_number": 0, "pos": 0, "word": "1"},
            {"index": 312, "element_number": 0, "pos": 4, "word": "eanadollui"},
            {"index": 370, "element_number": 0, "pos": 4, "word": "eanadollui"},
            {"index": 586, "element_number": 0, "pos": 4, "word": "eanadollui"},
            {"index": 1130, "element_number": 0, "pos": 2, "word": "ruvnno"},
            {"index": 1197, "element_number": 0, "pos": 1, "word": "miljon"},
            {"index": 1276, "element_number": 0, "pos": 4, "word": "eanadollui"},
        ],
    ]
