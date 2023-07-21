import discord
import json
import time
from pathlib import Path


class SpotifyRecords:
    def __init__(self):
        self._path = Path("./spotify_records.json")
        self._records = None

    def add_to_record(self, track: discord.Spotify, member: discord.Member) -> None:
        if not self._records:
            self._read_records()

        self._records['records'].append({
            'discord_user_id': member.id,
            'track_id': track.track_id,
            'timestamp': time.time()
        })

        with open(self._path, 'w+') as f:
            f.write(json.dumps(self._records, indent=4))
        
        self._read_records()

    def _read_records(self) -> None:
        if not self._path.exists():
            self._records = {'records': []}

            with open(self._path, 'w+') as f:
                f.write(json.dumps(self._records, indent=4))
        
        
        with open(self._path, 'r') as f:
            self._records = json.loads(f.read())

    def get_records_for_cache(self) -> list[str]:
        if not self._records:
            self._read_records()
        
        return [x['track_id'] for x in self._records['records']]


class SpotifyCache:
    def __init__(self):
        self._cache = []

    def old_cache(self) -> None:
        self._cache += SpotifyRecords().get_records_for_cache()

    def in_cache(self, track_id: str) -> bool:
        return track_id in self._cache
    
    def add_to_cache(self, track_id: str) -> None:
        self._cache.append(track_id)

    @staticmethod
    def build_embed(track: discord.Spotify, member: discord.Member, client: discord.Client) -> discord.Embed:
        e = discord.Embed(title=track.title, url=track.track_url)
        e = e.set_image(url=track.album_cover_url)
        e = e.add_field(name="Album", value=track.album)
        e = e.add_field(name="Artist", value=str(track.artists)[1:-1].replace("'", ''))
        e = e.add_field(name="Listened to by", value=member.name, inline=False)
        e = e.set_footer(text="ChaluBot", icon_url=client.user.display_avatar.url)
        e.color = discord.Color.from_str("#FF9A62")

        SpotifyRecords().add_to_record(track, member)

        return e
