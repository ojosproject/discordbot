import json
import os


class DataStorage:
    def __init__(self, prod: bool = False):
        self._prod = prod

    @staticmethod
    def get_server_data(server_id: int = None) -> dict:
        with open("./data/server_data.json", "r") as f:
            if server_id:
                return json.loads(f.read())[server_id]
            else:
                return json.loads(f.read())

    def get_token(self) -> str:
        if self._prod:
            with open("./.vscode/launch.json") as f:
                return json.loads(f.read())['configurations']['env']['BOT_TOKEN']
        else:
            return os.getenv("DEV_BOT_TOKEN")
