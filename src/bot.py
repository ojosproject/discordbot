import discord
import os
from data import Data
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True


SERVER_WHITELIST = [1204178277720268901]
CARLOS_ID = 458773298961055758


class Sauron(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.data = Data("data.json")


    async def on_ready(self):
        print(f"Ready to go, @{self.application.owner.name}!")

    async def setup_hook(self):
        for guild_id in SERVER_WHITELIST:
            print(f"Updated {guild_id} commands.")
            await self.tree.sync(guild=discord.Object(id=guild_id))


# Commands begin below.
client = Sauron(intents=intents)

@client.tree.command(name="assign",
                     description="Assign a research paper to a team member.",
                     guilds=[discord.Object(id=server_id) for server_id in SERVER_WHITELIST])
async def assign(interaction: discord.Interaction):
    try:
        ...
    except discord.HTTPException:
        await interaction.response.send_message("Sorry, I had an unexpected error. :/", delete_after=10)

@client.tree.command(name="claim",
                     description="Claim a research paper for yourself!",
                     guilds=[discord.Object(id=server_id) for server_id in SERVER_WHITELIST])
async def claim(interaction: discord.Interaction):
    try:
        ...
    except discord.HTTPException:
        await interaction.response.send_message("Sorry, I had an unexpected error. :/", delete_after=10)


client.run(os.getenv("DISCORD_TOKEN"))
