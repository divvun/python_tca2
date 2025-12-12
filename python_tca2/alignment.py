from pathlib import Path
from typing import Literal

import typer

from python_tca2 import alignmentmodel
from python_tca2.anchorwordlist import AnchorWordList
from python_tca2.tmx import write_tmx_result

app = typer.Typer()


@app.command()
def main(
    text_file1: str = typer.Option(
        ..., "--text-file1", help="First text file"
    ),
    text_file2: str = typer.Option(
        ..., "--text-file2", help="Second text file"
    ),
    text_file1_lang: str = typer.Option(
        ..., "--text-file1-lang", help="Language code for first text file"
    ),
    text_file2_lang: str = typer.Option(
        ..., "--text-file2-lang", help="Language code for second text file"
    ),
    anchor_file: str | None = typer.Option(
        None, "--anchor-file", help="Anchor word list file"
    ),
    output_format: Literal["tmx", "html"] = typer.Option(
        "html", "--output-format", help="Output format"
    ),
) -> None:
    anchor_word_list = AnchorWordList()
    if anchor_file is not None:
        anchor_word_list.load_from_file(anchor_file)

    aligner = alignmentmodel.AlignmentModel(
        sentences_tuple=(
            Path(text_file1).read_text().splitlines(),
            Path(text_file2).read_text().splitlines(),
        ),
        anchor_word_list=anchor_word_list,
    )

    aligned = aligner.suggest_without_gui()

    write_tmx_result(
        file1_path=Path(text_file1),
        language_pair=(text_file1_lang, text_file2_lang),
        non_empty_sentence_pairs=aligned.non_empty_pairs(),
        output_format=output_format,
    )


if __name__ == "__main__":
    app()
