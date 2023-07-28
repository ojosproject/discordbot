import json
import os


class DataStorage:
    def __init__(self, prod: bool = False):
        self._prod = prod

    @staticmethod
    def get_server_data(server_id: int = None, *, with_feature: str = None) -> dict:
        """
        Returns a dict of server data.

        :param server_id: The server ID. If empty, returns all server data.
        :param with_feature: Returns servers with only specific features enabled. For slash commands, ensure it has
        "commands:COMMAND_NAME" to get a specific command.
        """
        with open("./data/server_data.json", "r") as f:
            all_data = json.loads(f.read())

            if server_id:
                assert not with_feature, "DataStorage.get_server_data: not with_feature to get individual server data."
                return all_data[server_id]
            else:
                if with_feature:
                    if ":" in with_feature:
                        assert with_feature.count(":") == 1, "DataStorage.get_server_data: Specific feature lookup must only have one :."
                        feature, command = with_feature.split(":")
                        return {s_id: s_data for s_id, s_data in all_data if s_data['features'][feature] and command in s_data['commands']}
                    else:
                        return {s_id: s_data for s_id, s_data in all_data if s_data['features'][with_feature]}
                else:
                    return all_data

    def get_token(self) -> str:
        if self._prod:
            with open("./.vscode/launch.json") as f:
                return json.loads(f.read())['configurations']['env']['BOT_TOKEN']
        else:
            return os.getenv("DEV_BOT_TOKEN")
