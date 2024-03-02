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
        """Initiates the Data class

        Args:
            file (str): The file that has data to use/change

        Raises:
            FileNotAvailableError: Raised if the file does not exist
        """
        if not Path(file).exists():
            raise FileNotAvailableError("Data.__init__: The file was not found on the server.")
    
        self._file: Path = Path(file)
        self._content = json.loads(self._file.read_text())

    def commit(self) -> None:
        """
        Saves the information in self._content to the self._file file.
        """
        with open(self._file, 'w+') as f:
            f.write(json.dumps(self._content, indent=4))

    def _readings_already_included(self, url: str) -> int:
        """Checks whether or not this is a duplicate reading with its URL.

        Args:
            url (str): The URL to search for

        Returns:
            int: Returns the index of the reading if it's included, -1 otherwise
        """
        for index, reading in enumerate(self._content['readings']):
            if reading['url'] == url:
                return index
        return -1

    def add_reading(self, title: str, url: str) -> None:
        """Adds a reading to self._content

        Args:
            title (str): The title of the paper
            url (str): The URL of the paper

        Raises:
            DuplicateReadingError: The reading is already included in self._content
        """
        if self._readings_already_included(url) != -1:
            raise DuplicateReadingError('Data.add_reading: The reading is already included.')

        self._content['readings'].append(
            {
                "id": len(self._content['readings']),
                "title": title,
                "url": url,
                "assigned_to": 0,
                "notes": "",
                "summary": "",
                "submitted": False
            }
        )

    def assign_reading(self, url: str, user_id: int) -> None:
        """Assigns a paper to an individual.

        Args:
            url (str): The URL that's waiting to be assigned
            user_id (int): A Discord user ID to assign the reading to

        Raises:
            ReadingNotFoundError: Raised if the URL is not in the system.
        """
        reading_index = self._readings_already_included(url)
        
        if reading_index == -1:
            raise ReadingNotFoundError("Reading does not exist.")

        self._content['readings'][reading_index].update({
            "assigned_to": user_id
        })

    def add_notes_and_summary(self, url: str, notes: str, summary: str) -> None:
        """Adds notes and a summary to a paper.

        Args:
            url (str): The URL to add the notes to
            notes (str): The notes
            summary (str): A summary of the paper itself

        Raises:
            ReadingNotFoundError: Raised when the URL is not in the system
            MissingAssigneeError: Raised when the referenced paper does not have an assignee
        """
        reading_index = self._readings_already_included(url)

        if reading_index == -1:
            raise ReadingNotFoundError("Reading does not exist.")

        if self._content['readings'][reading_index]['assigned_to'] == 0:
            raise MissingAssigneeError('Data.add_notes_and_summary: Cannot add content without assigned user.')
        
        self._content['readings'][reading_index].update({
            "notes": notes,
            "summary": summary
        })

    def git(self, url: str) -> None:
        """Writes up instructions to eventually deliver to git

        Args:
            url (str): The URL that should be committed to the git repository

        Raises:
            MissingNotesError: Raised if the paper does not have notes or a summary
        """
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
            
    def get_content(self) -> dict:
        """Returns a copy of the data.

        Returns:
            dict: A copy of the data.
        """
        return dict(self._content)
    
    def get_paper(self, paper_id: int) -> dict:
        for paper in self._content['readings']:
            if paper['id'] == paper_id:
                return paper
            
        raise ReadingNotFoundError
