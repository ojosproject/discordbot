import discord
from discord import Embed, app_commands

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

SPOTIFY_CACHE = []

class ChaluBot(discord.Client):
    def __init__(self, *,intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        await self.change_presence(status=discord.Status.online, activity=discord.Game("with my food"))
        print("Ready to go!")

    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        global SPOTIFY_CACHE
        if before.guild.id == SERVERS['ChaluBot Developers']['id'] and after.activity and after.activity.name == 'Spotify':
            after.activity: discord.Spotify
            if after.activity.track_id not in SPOTIFY_CACHE:
                e = Embed(title=after.activity.title, url=after.activity.track_url)
                e = e.set_image(url=after.activity.album_cover_url)
                e = e.add_field(name="Album", value=after.activity.album)
                e = e.add_field(name="Artist", value=str(after.activity.artists)[1:-1].replace("'", ''))
                e = e.add_field(name="Listened to by", value=after.name, inline=False)
                e = e.set_footer(text="ChaluBot", icon_url=self.user.display_avatar.url)
                e.color = discord.Color.from_str("#FF9A62")

                # prevents repeats
                SPOTIFY_CACHE.append(after.activity.track_id)

                await self.get_channel(SERVERS['ChaluBot Developers']['spotify_channel_id']).send("", embeds=[e])

    async def setup_hook(self):
        for s, o in SERVERS.items():
            await self.tree.sync(guild=o['object'])
            print(f"Updated {s} commands.")


client = ChaluBot(intents=intents)
