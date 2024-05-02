import json

import click

from python_tca2 import alignmentmodel


def parallelize(anchor_file, files: list[str]):
    model = alignmentmodel.AlignmentModel(keys=range(len(files)))

    model.anchor_word_list.load_from_file(anchor_file)
    for index, filename in enumerate(files):
        model.load_text(filename, index)

    model.suggets_without_gui()
    print(json.dumps(model.aligned.to_json(), indent=2, ensure_ascii=False))
    model.save_plain()


@click.command()
@click.argument("anchor_file")
@click.argument("text_file1")
@click.argument("text_file2")
def main(anchor_file, text_file1, text_file2):
    parallelize(anchor_file, files=[text_file1, text_file2])
