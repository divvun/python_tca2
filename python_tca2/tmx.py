from lxml import etree


def add_filename_id(filename):
    """Add the tmx filename as an prop element in the header."""
    prop = etree.Element("prop")
    prop.attrib["type"] = "x-filename"
    prop.text = filename

    return prop


def make_tuv(line: str, lang: str) -> etree._Element:
    """Make a tuv element given an input line and a lang variable."""
    tuv = etree.Element("tuv")
    tuv.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = lang
    seg = etree.Element("seg")
    seg.text = line.strip()
    tuv.append(seg)

    return tuv


def make_tmx_header(filename: str, lang: str) -> etree._Element:
    """Make a tmx header based on the lang variable."""
    header = etree.Element("header")

    # Set various attributes
    header.attrib["segtype"] = "sentence"
    header.attrib["o-tmf"] = "OmegaT TMX"
    header.attrib["adminlang"] = "en-US"
    header.attrib["srclang"] = lang
    header.attrib["datatype"] = "plaintext"

    header.append(add_filename_id(filename))

    return header


def make_tu(tuv_infos: tuple[tuple[str, str], ...]) -> etree._Element:
    """Make a tmx tu element based on line and language tuples."""
    transl_unit = etree.Element("tu")

    for line, lang in tuv_infos:
        transl_unit.append(make_tuv(line, lang))

    return transl_unit


def make_tmx(
    file1_name: str,
    language_pair: tuple[str, str],
    non_empty_sentence_pairs: list[tuple[str, str]],
) -> etree._Element:
    """Make tmx file based on the output of the aligner."""
    tmx = etree.Element("tmx")
    header = make_tmx_header(
        file1_name,
        language_pair[0],
    )
    tmx.append(header)

    body = etree.SubElement(tmx, "body")
    for sentence_pair in non_empty_sentence_pairs:
        transl_unit = make_tu(
            tuple(
                (sentence, language)
                for (sentence, language) in zip(
                    sentence_pair, language_pair, strict=True
                )
            )
        )
        body.append(transl_unit)

    return tmx
