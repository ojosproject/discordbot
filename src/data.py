# data.py
# Ojos Project
# 
# Helps manage data for the bot.
# The file that contains the data must be in JSON format.
import json
from pathlib import Path

class FileNotAvailableError(Exception):
    ...

class Data:
    _file: Path
    _content: dict

    def __init__(self, file: str):
        if not Path(file).exists():
            raise FileNotAvailableError("Data.__init__: The file was not found on the server.")
    
        self._file: Path = Path(file)
        self._content = json.load(self._file)

    def commit(self) -> None:
        with open(self._file, 'w+') as f:
            f.write(json.dumps(self._content))

    def _readings_already_included(self, url: str) -> int:
        for index, reading in enumerate(self._content['readings']):
            if reading['url'] == url:
                return index
        return -1

    def add_reading(self, title: str, url: str) -> None:
        assert self._readings_already_included(url) == -1, 'Data.add_reading: The reading is already included.'

        self._content['readings'].append(
            {'title': title,
             'url': url,
             'assigned_to': None}
        )

    def assign_reading(self, url: str, user_id: int | None) -> None:
        reading_index = self._readings_already_included(url)
        
        if reading_index == -1:
            raise Exception("Reading does not exist.")

        reading = self._content[reading_index]
        self._content['readings'].pop(reading_index)
        # add the new version
        self._content['readings'].append({
            'title': reading['title'],
            'url': reading['url'],
            'assigned_to': user_id
        })
