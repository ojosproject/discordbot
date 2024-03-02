# bot.py
# Ojos Project
# 
# A Discord bot designed to help organize the Research team.
import discord
import os
from data import Data, DuplicateReadingError, MissingNotesError, ReadingNotFoundError
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True

# important constants
SERVER_WHITELIST = [1204178277720268901]
CARLOS_ID = 458773298961055758
RESEARCH_TEAM_ID = 1204340599403323442
OJOS_TEAM_ID = 1204179952099139604


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

@client.tree.command(name="add",
                    description="Add a research paper for later",
                    guilds=[discord.Object(id=server_id) for server_id in SERVER_WHITELIST])
@app_commands.describe(
    title="What is the title of this paper?",
    url="What is the Google Drive URL?"
)
async def add(interaction: discord.Interaction, title: str, url: str):
    try:
        client.data.add_reading(title, url)
        client.data.commit()
        await interaction.response.send_message(f":white_check_mark: Done! Added [{title}]({url}). If you'd like to claim this reading, please use `/claim`!")
    except DuplicateReadingError:
        await interaction.response.send_message(":x: Sorry, this article is already registered.", ephemeral=True, delete_after=10)
    except discord.HTTPException:
        await interaction.response.send_message(":question: Sorry, I had an unexpected error...")


@client.tree.command(name="list",
                    description="View all the research papers we've looked into so far.",
                    guilds=[discord.Object(id=server_id) for server_id in SERVER_WHITELIST])
async def list_papers(interaction: discord.Interaction):
    data = client.data.get_content()

    try:
        embed = discord.Embed(
            title="Research Papers",
            description="These are the research papers for the Research team."
        )

        for paper in data['readings']:
            embed.add_field(
                name="Title",
                value=f"[{paper['title'][:35]}... (#{paper['id']})]({paper['url']})",
                inline=True
            )

            assigned = "Nobody"

            if paper['assigned_to']:
                assigned = interaction.guild.get_member(paper['assigned_to']).display_name

            embed.add_field(
                name="Assigned to",
                value=assigned,
                inline=True
            )

            finished = ":x: No"
            if paper['notes'] and paper['summary']:
                finished = ":white_check_mark: Yes!"

            embed.add_field(
                name="Finished?",
                value=finished,
                inline=True
            )
            
            embed.add_field(
                name=" ",
                value=" ",
                inline=False
            )

        await interaction.response.send_message(content="", embeds=[embed])

    except discord.HTTPException:
        await interaction.response.send_message(":question: Sorry, I had an unexpected error...")



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

            client.data.assign_reading(paper['url'], member.id)
            client.data.commit()
            await interaction.response.send_message(f"{member.mention}, you've been assigned the following reading: [{paper['title']}]({paper['url']})")
        else:
            await interaction.response.send_message(":x: Sorry, but only Carlos can use this command.", ephemeral=True, delete_after=10)
    except ReadingNotFoundError:
        await interaction.response.send_message(":question: The Paper ID was not found in the system.", ephemeral=True, delete_after=10)
    except discord.HTTPException:
        await interaction.response.send_message("Sorry, I had an unexpected error. :/", delete_after=10)

@client.tree.command(name="claim",
                    description="Claim a research paper.",
                    guilds=[discord.Object(id=server_id) for server_id in SERVER_WHITELIST])
@app_commands.describe(
    paper_id="The paper to claim."
)
async def claim(interaction: discord.Interaction, paper_id: int):
    try:
        paper = client.data.get_paper(paper_id)

        client.data.assign_reading(paper['url'], interaction.user.id)
        client.data.commit()
        await interaction.response.send_message(f"{interaction.user.mention}, you've been assigned the following reading: [{paper['title']}]({paper['url']})")
    except ReadingNotFoundError:
        await interaction.response.send_message(":question: The Paper ID was not found in the system.", ephemeral=True, delete_after=10)
    except discord.HTTPException:
        await interaction.response.send_message("Sorry, I had an unexpected error. :/", delete_after=10)

@client.tree.command(name="commit",
                    description="Finished your research? Commit it!",
                    guilds=[discord.Object(id=server_id) for server_id in SERVER_WHITELIST])
@app_commands.describe(
    paper_id="The paper to finalize."
)
async def commit(interaction: discord.Interaction, paper_id: int):
    try:
        paper = client.data.get_paper(paper_id)

        client.data.git(
            paper['url']
        )

        await interaction.response.send_message(f"Your notes will be published soon once ${interaction.guild.get_member(CARLOS_ID).mention} gets on the computer. Thank you, ${interaction.user.mention}!")
    except MissingNotesError:
        await interaction.response.send_message(f":x: You need to add both notes and summary to make public.", ephemeral=True, delete_after=10)
    except discord.HTTPException:
        await interaction.response.send_message("Sorry, I had an unexpected error. :/", delete_after=10)


client.run(os.getenv("DISCORD_TOKEN"))
