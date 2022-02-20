from pathlib import Path
import time


class FileCacheItem(object):
    def __init__(self, file: Path):
        self.file = file
        self.contents = file.read_text()
        self.last_access = time.time()
        self.mutated_contents = None
        self.mutated = False

    @property
    def is_stale(self):
        return self.file.stat().st_mtime > self.last_access


class FileCache(object):
    def __init__(self):
        self._cache = {}

    def _is_in_cache(self, file: Path):
        key = str(file)
        if key not in self._cache:
            return False
        return not self._cache[key].is_stale

    def _get_from_cache(self, file: Path):
        return self._cache[str(file)]

    def _insert_into_cache(self, file: Path):
        self._cache[str(file)] = FileCacheItem(file)

    def _read_file_get_item(self, file: Path):
        file = file.resolve()
        if not self._is_in_cache(file):
            self._insert_into_cache(file)
        return self._get_from_cache(file)

    def read_file(self, file: Path):
        return self._read_file_get_item(file).contents

    def read_file_as_type(self, file: Path, builder):
        item = self._read_file_get_item(file)
        if not item.mutated:
            item.mutated_contents = builder(item.contents)
        return item.mutated_contents
