from pathlib import Path
from typing import Literal

import typer

from python_tca2 import alignmentmodel
from python_tca2.anchorwordlist import AnchorWordList
from python_tca2.tmx import write_streaming_result

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

    with Path(text_file1).open(encoding="utf-8") as first_file, Path(
        text_file2
    ).open(encoding="utf-8") as second_file:
        aligner = alignmentmodel.AlignmentModel(
            sentences_tuple=(first_file, second_file),
            anchor_word_list=anchor_word_list,
        )
        write_streaming_result(
            file1_path=Path(text_file1),
            language_pair=(text_file1_lang, text_file2_lang),
            alignments=aligner.iter_alignment_elements(),
            output_format=output_format,
        )


if __name__ == "__main__":
    app()
