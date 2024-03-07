# bot.py
# Ojos Project
# 
# A Discord bot designed to help organize the Research team.
import discord
import os
from ResearchEmbed import ResearchEmbed
from data import Data, DuplicatePaperError, MissingNotesError, PaperNotFoundError
from discord import app_commands
from pathlib import Path

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True

# important constants
SERVER_WHITELIST = [1204178277720268901]
CARLOS_ID = 458773298961055758
RESEARCH_TEAM_ID = 1204340599403323442
OJOS_TEAM_ID = 1204179952099139604


class Bot(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        assert Path("data.json").exists(), "ChaluBot.__init__: The `data.json` file cannot be found."

        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.data = Data("data.json")


    async def on_ready(self):
        print(f"Ready to go, @{self.application.owner.name}!")

    async def setup_hook(self):
        for guild_id in SERVER_WHITELIST:
            print(f"Updated {guild_id} commands.")
            await self.tree.sync(guild=discord.Object(id=guild_id))


# Models begin below.

class Notes(discord.ui.Modal):
    summary = discord.ui.TextInput(
        label='Summary',
        style=discord.TextStyle.long,
        placeholder='Summary of the research paper...',
    )

    notes = discord.ui.TextInput(
        label="Notes",
        style=discord.TextStyle.long,
        placeholder="Your notes in bullet points...",
    )

    def __init__(self, data: Data, paper_id: int):
        super().__init__(title='Notes')
        self._data = data
        self._paper = data.get_paper(paper_id)

        self.summary.default = self._paper['summary']
        self.notes.default = self._paper['notes']


    async def on_submit(self, interaction: discord.Interaction):
        self._data.add_notes_and_summary(
            url=self._paper['url'],
            notes=self.notes.value,
            summary=self.summary.value
        )

        self._data.commit()
        await interaction.response.send_message(f"Done! Thank you for the notes, {interaction.user.mention}! If you think this is ready to publish, go ahead and try `/commit {self._paper['id']}`.\n\n__Your notes for [{self._paper['title']}]({self._paper['url']}):__\n\n{self._paper['notes']}\n\n__Your summary:__\n{self._paper['summary']}")




# Commands begin below.
client = Bot(intents=intents)

@client.tree.command(name="add_paper",
                    description="Add a research paper for later",
                    guilds=[discord.Object(id=server_id) for server_id in SERVER_WHITELIST])
@app_commands.describe(
    title="What is the title of this paper?",
    url="What is the Google Drive URL?"
)
async def add_paper(interaction: discord.Interaction, title: str, url: str):
    try:
        if OJOS_TEAM_ID in [x.id for x in interaction.user.roles]:
            client.data.add_paper(title, url)
            client.data.commit()
            await interaction.response.send_message(f":white_check_mark: Done! Added [{title}]({url}). If you'd like to claim this reading, please use `/claim`!")
        else:
            await interaction.response.send_message(":x: Sorry, but you're not authorized to use this command.", ephemeral=True, delete_after=10)
    except DuplicatePaperError:
        await interaction.response.send_message(":x: Sorry, this article is already registered.", ephemeral=True, delete_after=10)
    except discord.HTTPException:
        await interaction.response.send_message(":question: Sorry, I had an unexpected error...", ephemeral=True, delete_after=10)


@client.tree.command(name="list",
                    description="View all the research papers we've looked into so far.",
                    guilds=[discord.Object(id=server_id) for server_id in SERVER_WHITELIST])
async def list_papers(interaction: discord.Interaction):
    data = client.data.get_db()

    try:
        await interaction.response.send_message(content="", embeds=[ResearchEmbed(data['papers']).discord_embed()], ephemeral=True)

    except discord.HTTPException:
        await interaction.response.send_message(":question: Sorry, I had an unexpected error...", ephemeral=True, delete_after=10)



@client.tree.command(name="assign",
                    description="Assign a research paper to a team member.",
                    guilds=[discord.Object(id=server_id) for server_id in SERVER_WHITELIST])
@app_commands.describe(
    member="The member to assign this to. They must have the Research team role.",
    paper_id="The paper to assign the individual."
)
async def assign(interaction: discord.Interaction, member: discord.Member, paper_id: int):
    try:
        if interaction.user.id == CARLOS_ID:
            paper = client.data.get_paper(paper_id)

            client.data.assign_paper(paper['url'], member.id)
            client.data.commit()
            await interaction.response.send_message(f"{member.mention}, you've been assigned the following reading: [{paper['title']}]({paper['url']})")
        else:
            await interaction.response.send_message(":x: Sorry, but only Carlos can use this command.", ephemeral=True, delete_after=10)
    except PaperNotFoundError:
        await interaction.response.send_message(":question: The Paper ID was not found in the system.", ephemeral=True, delete_after=10)
    except discord.HTTPException:
        await interaction.response.send_message("Sorry, I had an unexpected error. :/", ephemeral=True, delete_after=10)


@client.tree.command(name="claim",
                    description="Claim a research paper.",
                    guilds=[discord.Object(id=server_id) for server_id in SERVER_WHITELIST])
@app_commands.describe(
    paper_id="The paper to claim."
)
async def claim(interaction: discord.Interaction, paper_id: int):
    try:
        if OJOS_TEAM_ID in [x.id for x in interaction.user.roles]:
            paper = client.data.get_paper(paper_id)

            client.data.assign_paper(paper['url'], interaction.user.id)
            client.data.commit()
            await interaction.response.send_message(f"{interaction.user.mention}, you've been assigned the following reading: [{paper['title']}]({paper['url']})")
        else:
            await interaction.response.send_message(":x: Sorry, but you're not authorized to use this command.", ephemeral=True, delete_after=10)
    except PaperNotFoundError:
        await interaction.response.send_message(":question: The Paper ID was not found in the system.", ephemeral=True, delete_after=10)
    except discord.HTTPException:
        await interaction.response.send_message("Sorry, I had an unexpected error. :/", ephemeral=True, delete_after=10)


@client.tree.command(name="commit",
                    description="Finished your research? Commit it!",
                    guilds=[discord.Object(id=server_id) for server_id in SERVER_WHITELIST])
@app_commands.describe(
    paper_id="The paper to finalize."
)
async def commit(interaction: discord.Interaction, paper_id: int):
    try:
        paper = client.data.get_paper(paper_id)

        if interaction.user.id == paper['assigned_to']:
            client.data.git(
                paper['url']
            )

            await interaction.response.send_message(f"Your notes will be published soon once {interaction.guild.get_member(CARLOS_ID).mention} gets on the computer. Thank you, {interaction.user.mention}!")
        else:
            await interaction.response.send_message(":x: Sorry, but you're not assigned to this paper.", ephemeral=True, delete_after=10)
    except MissingNotesError:
        await interaction.response.send_message(f":x: You need to add both notes and summary to make public.", ephemeral=True, delete_after=10)
    except discord.HTTPException:
        await interaction.response.send_message("Sorry, I had an unexpected error. :/", ephemeral=True, delete_after=10)


@client.tree.command(name="add_notes",
                    description="Add notes to a research document",
                    guilds=[discord.Object(id=server_id) for server_id in SERVER_WHITELIST])
@app_commands.describe(
    paper_id="The paper to add notes to."
)
async def add_notes(interaction: discord.Interaction, paper_id: int):
    if interaction.user.id == client.data.get_paper(paper_id)['assigned_to']:
        await interaction.response.send_modal(Notes(client.data, paper_id))
    else:
        await interaction.response.send_message(":x: Sorry, but you're not assigned to this paper.", ephemeral=True, delete_after=10)

@client.tree.command(name="help",
                    description="Gives you the link to the docs website.",
                    guilds=[discord.Object(id=server_id) for server_id in SERVER_WHITELIST])
async def send_help(interaction: discord.Interaction):
    await interaction.response.send_message("https://docs.ojosproject.org/teams/research/chalubot", ephemeral=True)


@client.tree.command(name="datafile",
                    description="Get the database file through a Discord DM.",
                    guilds=[discord.Object(id=server_id) for server_id in SERVER_WHITELIST])
async def datafile(interaction: discord.Interaction):
    if interaction.user.id == CARLOS_ID:
        file_path = client.data.save_db_to_drive()

        await interaction.user.send(
            content="NOTICE: THIS IS PRIVATE INFORMATION, AND SHOULD BE TREATED AS SUCH.\n\nHere's the requested `data.json` file:",
            file=discord.File(file_path),
            delete_after=10
        )

        os.remove(file_path)

        await interaction.response.send_message(":white_check_mark: Operation succeeded.", ephemeral=True, delete_after=10)

    else:
        await interaction.response.send_message(":x: This command can only be used by Carlos."\
                                                "\n\n__Curious about how the command works?__\n"\
                                                "This command sends Carlos a private `data.json` file. It contains "\
                                                "all of the research information we have. It is encrypted with "\
                                                "[GPG](https://en.wikipedia.org/wiki/GNU_Privacy_Guard),"\
                                                " so you don't have to worry about your data being stolen.",
                                                ephemeral=True)


client.run(os.getenv("DISCORD_TOKEN"))
