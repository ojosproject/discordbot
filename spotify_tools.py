import discord
from data_tools import SpotifyDB


def get_spotify_activity(member: discord.Member) -> discord.Spotify | None:
    """
    If a member is streaming a track on Spotify, it returns the Activity. Does not include song files from their local device.
    """
    for activity in member.activities:
        if isinstance(activity, discord.Spotify) and activity.track_id:
            return activity


class SpotifyCache:
    def __init__(self):
        self._cache = []

    def old_cache(self) -> None:
        self._cache += SpotifyDB().get_records_for_cache()

    def in_cache(self, track_id: str, user_id: int) -> bool:
        return hash((track_id, user_id)) in self._cache
    
    def add_to_cache(self, track: discord.Spotify, member: discord.Member) -> None:
        SpotifyDB().add_to_record(track, member)
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
