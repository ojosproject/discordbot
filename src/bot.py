import discord
import os
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True


SERVER_WHITELIST = []
CARLOS_ID = 458773298961055758


class Sauron(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)


    async def on_ready(self):
        print(f"Ready to go, @{self.application.owner.name}!")

    async def setup_hook(self):
        for guild_id in SERVER_WHITELIST:
            print(f"Updated {guild_id} commands.")
            await self.tree.sync(guild=discord.Object(id=guild_id))


# Commands begin below.
client = Sauron(intents=intents)

client.run(os.getenv("DISCORD_TOKEN"))
