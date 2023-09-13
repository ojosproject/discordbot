import discord
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True


BS3D_GUID_ID = 1128184237535805442


class ChaluBot(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)


    async def on_ready(self):
        await self.change_presence(status=discord.Status.online, activity=discord.Game("with my food"))
        print("Ready to go!")

    async def setup_hook(self):
        await self.tree.sync(guild=discord.Object(id=BS3D_GUID_ID))


# Commands begin below.
client = ChaluBot(intents=intents)

@client.tree.command(name="ticket",
                     description="Want to report a bug or request a feature? Use this command!",
                     guilds=[discord.Object(id=BS3D_GUID_ID)])
async def new_issue(intraction: discord.Interaction):
    ...
    

client.run("")
