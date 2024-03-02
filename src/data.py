# data.py
# Ojos Project
# 
# Helps manage data for the bot.
# The file that contains the data must be in JSON format.
import json
import time
from pathlib import Path

class FileNotAvailableError(Exception):
    ...

class ReadingNotFoundError(Exception):
    ...

class DuplicateReadingError(Exception):
    ...

class MissingAssigneeError(Exception):
    ...

class MissingNotesError(Exception):
    ...

class Data:
    _file: Path
    _content: dict

    def __init__(self, file: str):
        if not Path(file).exists():
            raise FileNotAvailableError("Data.__init__: The file was not found on the server.")
    
        self._file: Path = Path(file)
        self._content = json.loads(self._file.read_text())

    def commit(self) -> None:
        with open(self._file, 'w+') as f:
            f.write(json.dumps(self._content, indent=4))

    def _readings_already_included(self, url: str) -> int:
        for index, reading in enumerate(self._content['readings']):
            if reading['url'] == url:
                return index
        return -1

    def add_reading(self, title: str, url: str) -> None:
        if self._readings_already_included(url) != -1:
            raise DuplicateReadingError('Data.add_reading: The reading is already included.')

        self._content['readings'].append(
            {
                "id": time.time(),
                "title": title,
                "url": url,
                "assigned_to": 0,
                "notes": "",
                "summary": "",
                "submitted": False
            }
        )

    def assign_reading(self, url: str, user_id: int | None) -> None:
        reading_index = self._readings_already_included(url)
        
        if reading_index == -1:
            raise ReadingNotFoundError("Reading does not exist.")

        self._content['readings'][reading_index].update({
            "assigned_to": user_id
        })

    def add_notes_and_summary(self, url, notes, summary) -> None:
        reading_index = self._readings_already_included(url)

        if reading_index == -1:
            raise ReadingNotFoundError("Reading does not exist.")

        if self._content['readings'][reading_index]['assigned_to'] == 0:
            raise MissingAssigneeError('Data.add_notes_and_summary: Cannot add content without assigned user.')
        
        self._content['readings'][reading_index].update({
            "notes": notes,
            "summary": summary
        })

    def git(self, url) -> None:
        reading_index = self._readings_already_included(url)

        data = self._content['readings'][reading_index]
        author_data = list(filter(lambda team_member: team_member['id'] == data['assigned_to'], self._content['team']))[0]

        if data['notes'] == "" or data['summary'] == "":
            raise MissingNotesError("Cannot commit without both notes and summary.")

        data['submitted'] = True
        self.commit()

        with open("src/templates/git_template.txt", "r") as f:
            template = f.read()

        with open(f"{data['id']}.txt", 'w+') as f:
            f.write(template
                    .replace("{TITLE}", data["title"])
                    .replace("{ID}", str(data['id']))
                    .replace("{NAME}", author_data['name'])
                    .replace("{EMAIL}", author_data['email']))
