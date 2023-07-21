import discord
from discord import app_commands
import os

intents = discord.Intents.default()
intents.message_content = True

SERVERS = {
    'ChaluBot Developers': discord.Object(id=1131618409382158366)
}

class ChaluBot(discord.Client):
    def __init__(self, *,intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        await self.change_presence(status=discord.Status.online, activity=discord.Game("with my food"))
        print("Ready to go!")

    async def setup_hook(self):
        for s, o in SERVERS.items():
            await self.tree.sync(guild=o)
            print(f"Updated {s} commands.")


client = ChaluBot(intents=intents)
client.run(os.getenv("BOT_TOKEN"))
