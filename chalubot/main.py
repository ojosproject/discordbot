import discord
from discord import app_commands
import os

MY_GUILD = discord.Object(id=1131618409382158366)

intents = discord.Intents.default()
intents.message_content = True

class ChaluBot(discord.Client):
    def __init__(self, *,intents: discord.Intents):
        super().__init__(intents=intents, command_prefix='/')
        self.tree = app_commands.CommandTree(self)


    async def on_ready(self):
        await self.change_presence(status=discord.Status.online, activity=discord.Game("with my food"))
        print("Ready to go!")

    async def setup_hook(self):
        await self.tree.sync(guild=MY_GUILD)
        await self.tree.sync(guild=discord.Object(id=1131553938949275738))


client = ChaluBot(intents=intents)


@client.tree.command(name="hello", description="I can say hello!!", guilds=[MY_GUILD])
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello!!", ephemeral=True)


@client.tree.command(name='wow', description='trying something new c:', guilds=[MY_GUILD])
async def wow(interaction: discord.Interaction):
    await interaction.response.send_message("yes!")

@client.tree.command(name='lastone', guilds=[discord.Object(id=1131553938949275738)])
async def last(interaction: discord.Interaction):
    await interaction.response.send_message("wooo")

client.run(os.getenv("BOT_TOKEN"))
