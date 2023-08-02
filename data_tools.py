import json
import os
import discord
import sqlite3
import time
from pathlib import Path
from collections import namedtuple


LAUNCH_FILE = Path("./.vscode/launch.json")
SERVER_DATA_FILE = Path("./data/server_data.json")
CHALUBOTDB_FILE = Path("./data/ChaluBotDB.db")
DEVELOPER_SERVER_ID = 1131618409382158366

RawSpotifyRecord = namedtuple('RawSpotifyRecord', ['discord_user_id', 'spotify_track_id', 'ts'])


class JSONData:
    def __init__(self, *, prod: bool = False, test_feature: str = None, append_to_beta: dict = None):
        if not prod:
            assert test_feature, "JSONData.__init__: test_feature must be selected if not in production."

        self._prod = prod
        self._test_feature = test_feature
        self._append_to_beta = append_to_beta

    def get_server_data(self, server_id: int = None, *, with_feature: str = None) -> dict:
        """
        Returns a dict of server data.

        :param server_id: The server ID. If empty, returns all server data.
        :param with_feature: Returns servers with only specific features enabled. For slash commands, ensure it has
        "commands:COMMAND_NAME" to get a specific command.
        """
        with open(SERVER_DATA_FILE, "r") as f:
            all_data = json.loads(f.read())
            if not self._prod:
                all_data = self._beta_data(all_data)

            if server_id:
                assert not with_feature, "DataStorage.get_server_data: not with_feature to get individual server data."
                return all_data[str(server_id)]
            else:
                if with_feature:
                    if ":" in with_feature:
                        assert with_feature.count(":") == 1, "DataStorage.get_server_data: Specific feature lookup must only have one :."
                        _, command = with_feature.split(":")
                        return {int(s_id): s_data for s_id, s_data in all_data.items() if command in s_data['features']['commands']}
                    else:
                        return {int(s_id): s_data for s_id, s_data in all_data.items() if s_data['features'][with_feature]}
                else:
                    return {int(s_id): s_data for s_id, s_data in all_data.items()}

    def get_token(self) -> str:
        if self._prod:
            with open(LAUNCH_FILE) as f:
                return json.loads(f.read())['configurations'][0]['env']['BOT_TOKEN']
        else:
            return os.getenv("DEV_BOT_TOKEN")
        
    def _beta_data(self, prod_data: dict) -> dict:
        dsid = str(DEVELOPER_SERVER_ID)
        beta_data = {dsid: prod_data[dsid]}
        if ":" in self._test_feature:
            assert self._test_feature.count(":") == 1, "DataStorage._beta_data: Specific feature lookup must only have one :."
            _, command = self._test_feature.split(":")
            beta_data[dsid]['features']['commands'] = [command]
        else:
            beta_data[dsid]['features'][self._test_feature] = True

        if self._append_to_beta:
            beta_data[dsid].update(self._append_to_beta)


        return beta_data
    
    def in_beta(self) -> bool:
        return not self._prod



class SpotifyDB:
    def __init__(self):
        self._path = CHALUBOTDB_FILE

    def add_to_record(self, track: discord.Spotify, member: discord.Member) -> None:
        with sqlite3.connect(self._path) as con:
            con.execute("INSERT INTO SpotifyRecords (discord_user_id, spotify_track_id, ts) VALUES(?, ?, ?);", (str(member.id), track.track_id, str(time.time())))

    def _read_records(self) -> list[RawSpotifyRecord]:
        with sqlite3.connect(self._path) as con:
            cursor = con.execute("SELECT * FROM SpotifyRecords;")
            return [RawSpotifyRecord(int(row[0]), row[1], float(row[2])) for row in cursor.fetchall()]

    def get_records_for_cache(self) -> list:
        return [hash((record.spotify_track_id, record.discord_user_id)) for record in self._read_records()]
