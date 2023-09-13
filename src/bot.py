import discord
import requests
import os
from discord import app_commands
from PKManager import generate_token

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True


BS3D_GUILD_ID = 1128184237535805442

REGISTERED_EMPLOYEES = {
    890992783689670679: "@Electric108",
    995196107506319510: "Isaiah S.",
    458773298961055758: "@calejvaldez"
}

class SubmitIssue(discord.ui.Modal):
    def __init__(self, label: str, *, title="Submit Issue", timeout=None, custom_id="submit_github_issue") -> None:
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)

        self.label = label

    feature = discord.ui.TextInput(
        label=f"What feature/bug fix would you like?",
        placeholder="Add birb dancing with money",
        row=0
    )

    page = discord.ui.TextInput(
        label="What page should this feature/bug fix be on?",
        placeholder="New page? URL?",
        row=1
    )

    deadline = discord.ui.TextInput(
        label="When should this get done by?",
        placeholder="Friday",
        row=2
    )

    async def on_submit(self, interaction: discord.Interaction):
        requester = REGISTERED_EMPLOYEES[interaction.user.id]

        body = f"> 🤖✌️ This was submitted using the [ChaluBot Discord bot](https://github.com/blackswan3dprinting/ChaluBot)!\n\n## What feature/bug fix would you like?\n{self.feature.value}\n\n## What page should this feature/bug fix be on?\n{self.page.value}\n\n## Please specify a deadline for this feature/bug fix to be done.\n{self.deadline.value}\n\n## Requested by\n{requester}"
        

        
        response = requests.post("https://api.github.com/repos/blackswan3dprinting/blackswan3d.com/issues",
                                    headers={"Accept": "application/vnd.github+json",
                                        "Authorization": f"Bearer {generate_token()}",
                                        "X-GitHub-Api-Version": "2022-11-28"},
                                    json={"title": self.feature.value,
                                        "body": body,
                                        "labels": [self.label],
                                        "assignees": ["calejvaldez"]})

        if response.status_code != 201:
            return await interaction.response.send_message(f"❌ Something seems to have gone wrong when using `/ticket`. Here's an error for {client.get_user(458773298961055758).mention}:\n\n```\n{response.text}\n```")

        response = response.json()
        return await interaction.response.send_message(f"✅ [Your issue]({response['html_url']}) has been successfully submitted. Thanks!", ephemeral=True)


class Dropdown(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label="Bug (something needs fixing)", value="bug", emoji="👨‍💻"),
            discord.SelectOption(label="Feature (add a new page or feature)", value="enhancement", emoji="💡")
        ]

        super().__init__(placeholder='Select a label...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SubmitIssue(label=self.values[0]))


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Dropdown())


class ChaluBot(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)


    async def on_ready(self):
        await self.change_presence(status=discord.Status.online, activity=discord.Game("with my food"))
        print("Ready to go!")

    async def setup_hook(self):
        await self.tree.sync(guild=discord.Object(id=BS3D_GUILD_ID))


# Commands begin below.
client = ChaluBot(intents=intents)

@client.tree.command(name="issues",
                     description="View all issues that have been opened on GitHub.",
                     guilds=[discord.Object(id=BS3D_GUILD_ID)])
async def view_issues(interaction: discord.Interaction):
    return await interaction.response.send_message("You can view all active issues [on GitHub](https://github.com/blackswan3dprinting/blackswan3d.com/issues).", ephemeral=True)

@client.tree.command(name="ticket",
                     description="Want to report a bug or request a feature? Use this command!",
                     guilds=[discord.Object(id=BS3D_GUILD_ID)])
async def new_issue(interaction: discord.Interaction):
    if interaction.user.id not in REGISTERED_EMPLOYEES:
        return await interaction.response.send_message("⚠️ Sorry, you're not registered to use this command.", ephemeral=True)
    
    await interaction.response.send_message(content="", view=DropdownView(), ephemeral=True)

client.run(os.getenv("DISCORD_TOKEN"))
