from pathlib import Path

import click

from python_tca2 import alignmentmodel
from python_tca2.anchorwordlist import AnchorWordList
from python_tca2.tmx import write_tmx_result


@click.command()
@click.option("--anchor_file", default=None, help="Anchor word list file")
@click.option(
    "--output_format",
    default="html",
    type=click.Choice(["tmx", "html"]),
    help="Output format",
)
@click.argument("text_file1")
@click.argument("text_file2")
@click.argument("text_file1_lang")
@click.argument("text_file2_lang")
def main(  # noqa: PLR0913
    anchor_file: str | None,
    output_format: str,
    text_file1: str,
    text_file2: str,
    text_file1_lang: str,
    text_file2_lang: str,
) -> None:
    anchor_word_list = AnchorWordList()
    if anchor_file is not None:
        anchor_word_list.load_from_file(anchor_file)

    aligner = alignmentmodel.AlignmentModel(
        text_pair=(Path(text_file1).read_text(), Path(text_file2).read_text()),
        anchor_word_list=anchor_word_list,
    )

    aligned, _ = aligner.suggest_without_gui()

    write_tmx_result(
        file1_path=Path(text_file1),
        language_pair=(text_file1_lang, text_file2_lang),
        non_empty_sentence_pairs=aligned.non_empty_pairs(),
        output_format=output_format,
    )
