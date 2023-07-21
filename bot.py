import discord
from discord import app_commands
from spotify_tools import SpotifyCache
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
    },
    "Wine Moms": {
        "id": 1131973022207725660,
        "object": discord.Object(id=1131973022207725660),
        "spotify_channel_id": 1131973048229187716
    }
}



class ChaluBot(discord.Client):
    def __init__(self, *,intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

        self._SPOTIFY_CACHE = SpotifyCache()

    async def on_ready(self):
        self._SPOTIFY_CACHE.old_cache()

        await self.change_presence(status=discord.Status.online, activity=discord.Game("with my food"))
        print("Ready to go!")

    async def on_presence_update(self, _, after: discord.Member):
        if after.guild.id in (SERVERS['Goobers']['id'], SERVERS['Wine Moms']['id']) and isinstance(after.activity, discord.Spotify) and after.activity.track_id and not self._SPOTIFY_CACHE.in_cache(after.activity.track_id, after.id):
            self._SPOTIFY_CACHE.add_to_cache(after.activity.track_id, after.id)
            
            for s in ('Goobers', 'Wine Moms'):
                await self.get_channel(SERVERS[s]['spotify_channel_id']).send("", embeds=self._SPOTIFY_CACHE.build_embed(after.activity, after, client))


    async def setup_hook(self):
        for s, o in SERVERS.items():
            await self.tree.sync(guild=o['object'])
            print(f"Updated {s} commands.")


client = ChaluBot(intents=intents)
client.run(os.getenv("BOT_TOKEN"))
