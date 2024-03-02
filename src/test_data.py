import unittest
import os
import json
from pathlib import Path
from data import Data, FileNotAvailableError, ReadingNotFoundError, DuplicateReadingError, MissingAssigneeError, MissingNotesError

class TestDataClass(unittest.TestCase):
    def setUp(self):
        with open('fake_data.json', 'w+') as f:
            f.write(
                json.dumps(
                    {
                        "readings": [],
                        "team": [
                            {
                                "id": 458773298961055758,
                                "name": "Carlos Valdez",
                                "email": "cvaldezh@uci.edu"
                            }
                        ]
                    }
                )
            )
        self.d = Data("fake_data.json")

    def test_error_on_non_existent_file(self):
        self.assertRaises(FileNotAvailableError, Data, "does_not_exit.jpeg")

    def test_file_opens_correctly(self):
        self.assertEqual(self.d._file, Path("fake_data.json"))

    def test_adding_reading(self):
        self.d.add_reading("Welcome", "https://ojosproject.org")

        self.assertEqual(
            (self.d._content['readings'][-1]['title'], self.d._content['readings'][-1]['url']),
            ('Welcome', 'https://ojosproject.org')
        )

    def test_assert_placeholder_content(self):
        self.d.add_reading('Welcome', 'https://ojosproject.org')
        test_content = self.d._content['readings'][-1]

        self.assertEqual(
            (test_content['assigned_to'], test_content['notes'], test_content['summary'], test_content['submitted']),
            (0, "", "", False)
        )

    def test_assign_reading(self):
        self.d.add_reading('Welcome', 'https://ojosproject.org')
        self.d.assign_reading('https://ojosproject.org', 458773298961055758)
        test_content = self.d._content['readings'][-1]

        self.assertEqual(
            test_content['assigned_to'],
            458773298961055758
        )

    def test_git(self):
        self.d.add_reading('Welcome', 'https://ojosproject.org')
        self.d.assign_reading('https://ojosproject.org', 458773298961055758)
        self.d.add_notes_and_summary('https://ojosproject.org', '# wowow', 'This is about Ojos Project dot org!')

        test_content = self.d._content['readings'][-1]

        self.d.git('https://ojosproject.org')

        with open(f"{test_content['id']}.txt", 'r') as f:
            self.assertEqual(
                f"---BEGIN COMMIT INSTRUCTIONS---\ngit add teams/research/work/{test_content['id']}.md\ngit commit --author \"Carlos Valdez <cvaldezh@uci.edu>\"\n---END COMMIT INSTRUCTIONS---\n\n---BEGIN COMMIT MESSAGE---\nfeat(research/work): added new research\n\nAdded notes for {test_content['title']}.\n\n\nCo-authored-by: Carlos Valdez <cvaldezh@uci.edu>\n---END COMMIT MESSAGE---",
                f.read()
            )
        
        os.remove(f"{test_content['id']}.txt")
        del self.d._content['readings'][-1]
        self.d.commit()

    def test_submit_be_true_after_git(self):
        self.d.add_reading('Welcome', 'https://ojosproject.org')
        self.d.assign_reading('https://ojosproject.org', 458773298961055758)
        self.d.add_notes_and_summary('https://ojosproject.org', '# wowow', 'This is about Ojos Project dot org!')

        test_content = self.d._content['readings'][-1]

        self.d.git('https://ojosproject.org')

        self.assertTrue(test_content['submitted'])

        os.remove(f"{test_content['id']}.txt")
        del self.d._content['readings'][-1]
        self.d.commit()

    def test_cannot_add_data_without_assignee(self):
        self.d.add_reading('Welcome', 'https://ojosproject.org')

        self.assertRaises(MissingAssigneeError, self.d.add_notes_and_summary, *('https://ojosproject.org', '# notes', 'summary'))

    def test_cannot_use_git_without_notes(self):
        self.d.add_reading('Welcome', 'https://ojosproject.org')
        self.d.assign_reading('https://ojosproject.org', 458773298961055758)

        self.assertRaises(MissingNotesError, self.d.git, 'https://ojosproject.org')

    def test_commit(self):
        self.d.add_reading('Welcome', 'https://ojosproject.org')
        self.d.assign_reading('https://ojosproject.org', 458773298961055758)
        self.d.add_notes_and_summary('https://ojosproject.org', '# wowow', 'This is about Ojos Project dot org!')
        self.d.commit()

        test_content = self.d._content['readings'][-1]

        with open('fake_data.json', 'r') as f:
            self.assertDictEqual(
                json.loads(f.read()),
                {
                    "readings": [
                        {
                            'id': test_content['id'],
                            'title': 'Welcome',
                            'url': 'https://ojosproject.org',
                            'assigned_to': 458773298961055758,
                            'notes': '# wowow',
                            'summary': 'This is about Ojos Project dot org!',
                            'submitted': False,
                        }
                    ],
                    "team": [
                        {
                            "id": 458773298961055758,
                            "name": "Carlos Valdez",
                            "email": "cvaldezh@uci.edu"
                        }
                    ]
                }
            )

    def test_same_reading_twice(self):
        self.d.add_reading("Whoa", "https://ojosproject.org")
        self.assertRaises(DuplicateReadingError, self.d.add_reading, *("W", "https://ojosproject.org"))

    def test_reading_not_found_error(self):
        self.assertRaises(ReadingNotFoundError, self.d.add_notes_and_summary, *('https://ojosproject.org', '# notes', 'summary'))


if __name__ == "__main__":
    unittest.main()
