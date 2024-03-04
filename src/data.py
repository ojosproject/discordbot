# data.py
# Ojos Project
# 
# Helps manage data for the bot.
# The file that contains the data must be in JSON format.
import json
import gnupg
import os
from pathlib import Path

class FileNotAvailableError(Exception):
    ...

class PaperNotFoundError(Exception):
    ...

class DuplicatePaperError(Exception):
    ...

class MissingAssigneeError(Exception):
    ...

class MissingNotesError(Exception):
    ...

class Data:
    _file: Path
    _db: dict

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
        self._db = json.loads(self._file.read_text())

    def commit(self) -> None:
        """
        Saves the information in self._db to the self._file file.
        """
        with open(self._file, 'w+') as f:
            f.write(json.dumps(self._db, indent=4))

    def _papers_already_included(self, url: str) -> int:
        """Checks whether or not this is a duplicate paper with its URL.

        Args:
            url (str): The URL to search for

        Returns:
            int: Returns the index of the paper if it's included, -1 otherwise
        """
        for index, paper in enumerate(self._db['papers']):
            if paper['url'] == url:
                return index
        return -1

    def add_paper(self, title: str, url: str) -> None:
        """Adds a paper to self._db

        Args:
            title (str): The title of the paper
            url (str): The URL of the paper

        Raises:
            DuplicatePaperError: The paper is already included in self._db
        """
        if self._papers_already_included(url) != -1:
            raise DuplicatePaperError('Data.add_paper: The paper is already included.')

        self._db['papers'].append(
            {
                "id": len(self._db['papers']),
                "title": title,
                "url": url,
                "assigned_to": 0,
                "notes": "",
                "summary": "",
                "submitted": False
            }
        )

    def assign_paper(self, url: str, user_id: int) -> None:
        """Assigns a paper to an individual.

        Args:
            url (str): The URL that's waiting to be assigned
            user_id (int): A Discord user ID to assign the paper to

        Raises:
            PaperNotFoundError: Raised if the URL is not in the system.
        """
        reading_index = self._papers_already_included(url)
        
        if reading_index == -1:
            raise PaperNotFoundError("Paper does not exist.")

        self._db['papers'][reading_index].update({
            "assigned_to": user_id
        })

    def add_notes_and_summary(self, url: str, notes: str, summary: str) -> None:
        """Adds notes and a summary to a paper.

        Args:
            url (str): The URL to add the notes to
            notes (str): The notes
            summary (str): A summary of the paper itself

        Raises:
            PaperNotFoundError: Raised when the URL is not in the system
            MissingAssigneeError: Raised when the referenced paper does not have an assignee
        """
        reading_index = self._papers_already_included(url)

        if reading_index == -1:
            raise PaperNotFoundError("Reading does not exist.")

        if self._db['papers'][reading_index]['assigned_to'] == 0:
            raise MissingAssigneeError('Data.add_notes_and_summary: Cannot add content without assigned user.')
        
        self._db['papers'][reading_index].update({
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
        reading_index = self._papers_already_included(url)

        data = self._db['papers'][reading_index]
        author_data = list(filter(lambda team_member: team_member['id'] == data['assigned_to'], self._db['team']))[0]

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
            
    def get_db(self) -> dict:
        """Returns a copy of the data.

        Returns:
            dict: A copy of the data.
        """
        return dict(self._db)
    
    def save_db_to_drive(self) -> str:
        gpg = gnupg.GPG()
        gpg.encrypt_file(
            "data.json",
            recipients="Carlos",
            passphrase=os.getenv("GPG_PASSPHRASE"),
            symmetric=True,
            output=f"{str(self._file)}.gpg"
        )

        return f"{str(self._file)}.gpg"
    
    def get_paper(self, paper_id: int) -> dict:
        for paper in self._db['papers']:
            if paper['id'] == paper_id:
                return paper
            
        raise PaperNotFoundError
