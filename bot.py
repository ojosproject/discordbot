import discord
from discord import Embed, app_commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True

SERVERS = {
    'ChaluBot Developers': {
        'id': 1131618409382158366,
        'object': discord.Object(id=1131618409382158366),
    },
    "Goobers": {
        "id": 1109362324386615336,
        "object": discord.Object(id=1109362324386615336),
        "spotify_channel_id": 1131861175550873621
    }
}


def build_song_embed(song: discord.Spotify, listener: str) -> discord.Embed:
    e = Embed(title=song.title, url=song.track_url)
    e = e.set_image(url=song.album_cover_url)
    e = e.add_field(name="Album", value=song.album)
    e = e.add_field(name="Artist", value=str(song.artists)[1:-1].replace("'", ''))
    e = e.add_field(name="Listened to by", value=listener, inline=False)
    e = e.set_footer(text="ChaluBot", icon_url=client.user.display_avatar.url)
    e.color = discord.Color.from_str("#FF9A62")

    return e


class ChaluBot(discord.Client):
    def __init__(self, *,intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.SPOTIFY_CACHE = []

    async def on_ready(self):
        await self.change_presence(status=discord.Status.online, activity=discord.Game("with my food"))
        print("Ready to go!")

    async def on_presence_update(self, _, after: discord.Member):
        if after.guild.id == SERVERS['Goobers']['id'] and isinstance(after.activity, discord.Spotify) and after.activity.track_id and after.activity.track_id not in self.SPOTIFY_CACHE:
            # prevents repeats
            self.SPOTIFY_CACHE.append(after.activity.track_id)

            await self.get_channel(SERVERS['Goobers']['spotify_channel_id']).send("", embeds=[build_song_embed(after.activity, after.name)])

    async def setup_hook(self):
        for s, o in SERVERS.items():
            await self.tree.sync(guild=o['object'])
            print(f"Updated {s} commands.")


client = ChaluBot(intents=intents)
client.run(os.getenv("BOT_TOKEN"))
