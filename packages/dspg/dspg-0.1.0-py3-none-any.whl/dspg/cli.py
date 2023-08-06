import os
import shutil
from pathlib import Path

from wikidata import client


import yaml

DATA_DIR = Path('data')
TEMP_DATA_DIR = Path('.temp/data')
wikidata = client.Client()


def add_wikidata(path: Path, lang):
    if path.is_dir():
        for child in path.iterdir():
            add_wikidata(child, lang)
    elif path.suffix == '.yml':
        with path.open('r') as f:
            data = yaml.load(f)
            if isinstance(data, list):
                for index, entry in enumerate(data):
                    if type(entry) == str and entry.startswith('Q'):
                        entity = wikidata.get(entry)
                        data[index] = {
                            'title': entity.label.texts[lang]
                        }
        path.unlink()
        with path.open('w') as f:
            yaml.dump(data, f)


def main():

    if TEMP_DATA_DIR.exists():
        shutil.rmtree(TEMP_DATA_DIR)
    shutil.copytree(DATA_DIR, TEMP_DATA_DIR)
    add_wikidata(TEMP_DATA_DIR, 'en')


if __name__ == '__main__':
    main()