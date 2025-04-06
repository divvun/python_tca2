import click
from lxml import etree

from python_tca2 import alignmentmodel


def parallelize(anchor_file, files: list[str]):
    model = alignmentmodel.AlignmentModel(
        {index: etree.parse(filename) for index, filename in enumerate(files)}
    )

    model.anchor_word_list.load_from_file(anchor_file)
    aligned, _ = model.suggest_without_gui()
    aligned.save_plain()


@click.command()
@click.argument("anchor_file")
@click.argument("text_file1")
@click.argument("text_file2")
def main(anchor_file, text_file1, text_file2):
    parallelize(anchor_file, files=[text_file1, text_file2])
