import discord
import time
import sqlite3
from pathlib import Path
from collections import namedtuple

RawSpotifyRecord = namedtuple('RawSpotifyRecord', ['discord_user_id', 'spotify_track_id', 'ts'])


def get_spotify_activity(member: discord.Member) -> discord.Spotify | None:
    """
    If a member is streaming a track on Spotify, it returns the Activity. Does not include song files from their local device.
    """
    for activity in member.activities:
        if isinstance(activity, discord.Spotify) and activity.track_id:
            return activity


class SpotifyRecords:
    def __init__(self):
        self._path = Path("./data/ChaluBotDB.db")

    def add_to_record(self, track: discord.Spotify, member: discord.Member) -> None:
        with sqlite3.connect(self._path) as con:
            con.execute("INSERT INTO SpotifyRecords (discord_user_id, spotify_track_id, ts) VALUES(?, ?, ?);", (str(member.id), track.track_id, str(time.time())))

    def _read_records(self) -> list[RawSpotifyRecord]:
        with sqlite3.connect("./data/ChaluBotDB.db") as con:
            cursor = con.execute("SELECT * FROM SpotifyRecords;")
            return [RawSpotifyRecord(int(row[0]), row[1], float(row[2])) for row in cursor.fetchall()]

    def get_records_for_cache(self) -> list:
        return [hash((record.spotify_track_id, record.discord_user_id)) for record in self._read_records()]


class SpotifyCache:
    def __init__(self):
        self._cache = []

    def old_cache(self) -> None:
        self._cache += SpotifyRecords().get_records_for_cache()

    def in_cache(self, track_id: str, user_id: int) -> bool:
        return hash((track_id, user_id)) in self._cache
    
    def add_to_cache(self, track: discord.Spotify, member: discord.Member) -> None:
        SpotifyRecords().add_to_record(track, member)
        self._cache.append(hash((track.track_id, member.id)))

    @staticmethod
    def build_embed(track: discord.Spotify, member: discord.Member, client: discord.Client) -> discord.Embed:
        e = discord.Embed(title=track.title, url=track.track_url)
        e = e.set_image(url=track.album_cover_url)
        e = e.add_field(name="Album", value=track.album)
        e = e.add_field(name="Artist", value=str(track.artists)[1:-1].replace("'", ''))
        e = e.add_field(name="Listened to by", value=member.name, inline=False)
        e = e.set_footer(text="ChaluBot", icon_url=client.user.display_avatar.url)
        e.color = discord.Color.from_str("#FF9A62")

        return e
