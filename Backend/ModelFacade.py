import subprocess
from pathlib import Path

from FileCache import FileCache
import yaml

from models.deck import Deck


def read_deck_file(s):
    return [Deck(x['deck']) for x in yaml.safe_load_all(s)]


def flatten_list(lists):
    o = []
    for i in lists:
        for j in i:
            o.append(j)
    return o


class ModelFacade(object):
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.cache = FileCache()
        self._decks = []
        self._try_pull_data()

    @property
    def _data_git_dir(self):
        return self.data_dir

    @property
    def _data_deck_dir(self):
        return self._data_git_dir / "decks"

    @property
    def _data_character_dir(self):
        return self._data_git_dir / "characters"

    def _data_needs_update(self):
        return not self._data_git_dir.exists()

    def _pull_data(self):
        print("Pulling data from github")
        subprocess.run(["git", "clone", "https://github.com/ncguy2/Sentinels-data", str(self._data_git_dir)])

    def _try_pull_data(self):
        print("Trying to pull data from github")
        if self._data_needs_update():
            self._pull_data()

    def _prepare_decks(self):
        if len(self._decks) == 0:
            for f in self._data_deck_dir.iterdir():
                self._decks.append(self.cache.read_file_as_type(f, read_deck_file))
            self._decks = flatten_list(self._decks)

    @property
    def decks(self):
        self._prepare_decks()
        return self._decks

    def get_deck_names(self):
        return [x.name for x in self.decks]

    def get_deck(self, deck_name):
        for x in self.decks:
            if deck_name == x.name:
                return x
        return None


