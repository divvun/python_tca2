import click

from python_tca2 import alignmentmodel

DEFAULT_MAX_PATH_LENGTH = 10
NUM_FILES = 2


class Alignment:
    def __init__(self):
        pass


@click.command()
@click.argument("anchor_file", type=click.File("r"))
@click.argument("text_file1", type=click.File("r"))
@click.argument("text_file2", type=click.File("r"))
def main(anchor_file, text_file1, text_file2):
    model = alignmentmodel.AlignmentModel()

    model.anchor_word_list.load_from_file(anchor_file)
    model.load_text(text_file1, 0)
    model.load_text(text_file2, 1)
