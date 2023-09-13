import discord
import requests
import os
from discord import app_commands
from typing import Literal

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True


BS3D_GUID_ID = 1128184237535805442
REGISTERED_EMPLOYEES = {
    890992783689670679: "@Electric108",
    995196107506319510: "Isaiah S.",
    458773298961055758: "@calejvaldez"
}


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

@client.tree.command(name="issues",
                     description="View all issues that have been opened on GitHub.",
                     guilds=[discord.Object(id=BS3D_GUID_ID)])
async def view_issues(interaction: discord.Interaction):
    return await interaction.response.send_message("You can view all active issues [on GitHub](https://github.com/blackswan3dprinting/blackswan3d.com/issues).", ephemeral=True)

@client.tree.command(name="ticket",
                     description="Want to report a bug or request a feature? Use this command!",
                     guilds=[discord.Object(id=BS3D_GUID_ID)])
@app_commands.describe(label="Is this a BUG or a FEATURE?",
                       request="What feature/bug fix would you like?",
                       page="What page should this feature/bug fix be on?",
                       deadline="Please specify a deadline for this feature/bug fix to be done.")
async def new_issue(interaction: discord.Interaction, label: Literal["bug", "feature"], request: str, page: Literal["All pages", "New page", "/about/", "/showcase/", "/our-team/"], deadline: str):
    if interaction.user.id not in REGISTERED_EMPLOYEES:
        return await interaction.response.send_message("⚠️ Sorry, you're not registered to use this command.", ephemeral=True)

    requester = REGISTERED_EMPLOYEES[interaction.user.id]
    label = label if label != "feature" else "enhancement"
    page_format = f"`{page}`" if "/" in page else page

    body = f"> 🤖✌️ This was submitted using the [ChaluBot Discord bot](https://github.com/blackswan3dprinting/ChaluBot)!\n\n## What feature/bug fix would you like?\n{request}\n\n## What page should this feature/bug fix be on?\n`{page_format}`\n\n## Please specify a deadline for this feature/bug fix to be done.\n{deadline}\n\n## Requested by\n{requester}"
    

    
    response = requests.post("https://api.github.com/repos/blackswan3dprinting/blackswan3d.com/issues",
                                headers={"Accept": "application/vnd.github+json",
                                    "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
                                    "X-GitHub-Api-Version": "2022-11-28"},
                                json={"title": request,
                                    "body": body,
                                    "labels": [label],
                                    "assignees": ["calejvaldez"]})

    if response.status_code != 201:
        return await interaction.response.send_message(f"❌ Something seems to have gone wrong when using `/ticket`. Here's an error for {client.get_user(458773298961055758).mention}:\n\n```\n{response.text}\n```")

    response = response.json()
    return await interaction.response.send_message(f"✅ [Your issue]({response['html_url']}) has been successfully submitted. Thanks!", ephemeral=True)

client.run(os.getenv("DISCORD_TOKEN"))
