from html import escape
from pathlib import Path
from typing import Iterable

from lxml import etree

from python_tca2.aligned_sentence_elements import (
    AlignedSentenceElements,
    to_string_tuple,
)


def add_filename_id(filename: str) -> etree.Element:
    """Add the tmx filename as an prop element in the header."""
    prop = etree.Element("prop")
    prop.attrib["type"] = "x-filename"
    prop.text = filename

    return prop


def make_tuv(line: str, lang: str) -> etree.Element:
    """Make a tuv element given an input line and a lang variable."""
    tuv = etree.Element("tuv")
    tuv.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = lang
    seg = etree.Element("seg")
    seg.text = line.strip()
    tuv.append(seg)

    return tuv


def make_tmx_header(filename: str, lang: str) -> etree.Element:
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


def make_tu(tuv_infos: tuple[tuple[str, str], ...]) -> etree.Element:
    """Make a tmx tu element based on line and language tuples."""
    transl_unit = etree.Element("tu")

    for line, lang in tuv_infos:
        transl_unit.append(make_tuv(line, lang))

    return transl_unit


def write_streaming_result(
    file1_path: Path,
    language_pair: tuple[str, str],
    alignments: Iterable[AlignedSentenceElements],
    output_format: str = "tmx",
) -> None:
    """Write aligned sentence pairs incrementally without retaining the corpus."""
    output_path = file1_path.with_suffix(f".{output_format}")

    if output_format == "tmx":
        with etree.xmlfile(output_path, encoding="utf-8") as output:
            output.write_declaration()
            with output.element("tmx"):
                output.write(make_tmx_header(file1_path.stem, language_pair[0]))
                with output.element("body"):
                    for alignment in alignments:
                        if all(alignment):
                            output.write(
                                make_tu(
                                    tuple(
                                        (sentence, language)
                                        for sentence, language in zip(
                                            to_string_tuple(alignment),
                                            language_pair,
                                            strict=True,
                                        )
                                    )
                                )
                            )
    elif output_format == "html":
        with output_path.open("w", encoding="utf-8") as output:
            output.write(
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                "<html><head><meta charset=\"UTF-8\"/></head>"
                "<body><table border=\"2\">\n"
            )
            for alignment in alignments:
                if all(alignment):
                    first, second = to_string_tuple(alignment)
                    output.write(
                        "<tr><td>"
                        f"{escape(first)}"
                        "</td><td>"
                        f"{escape(second)}"
                        "</td></tr>\n"
                    )
            output.write("</table></body></html>\n")
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

    print(f"Wrote {output_path}")
