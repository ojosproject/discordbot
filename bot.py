import discord
from discord import app_commands
from spotify_tools import SpotifyCache, get_spotify_activity
import os
import json

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True

with open('./data/server_data.json', 'r') as file:
    SERVERS: dict = json.loads(file.read())


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
        activity = get_spotify_activity(after)
        if not activity:
            return
        
        with_spotify = [server for server in SERVERS.values() if server['features']['spotify']]
        if after.guild.id in [server['id'] for server in with_spotify] and not self._SPOTIFY_CACHE.in_cache(activity.track_id, after.id):
            self._SPOTIFY_CACHE.add_to_cache(activity, after)

            [await self.get_channel(g['channel_ids']['spotify']).send("", embeds=[SpotifyCache.build_embed(activity, after, client)]) for g in with_spotify if after in self.get_guild(g['id']).members]


    async def setup_hook(self):
        for s, o in SERVERS.items():
            if o['features']['commands']:
                await self.tree.sync(guild=discord.Object(id=o['id']))
                print(f"Updated {s} commands.")


# Commands begin below.
client = ChaluBot(intents=intents)

def has_command(command_name: str, server_data: dict) -> bool:
    return server_data['features']['commands'] and command_name in server_data['features']['commands']


@client.tree.command(name="purge",
                     description="A classic purge command! 50 messages at a time.",
                     guilds=[discord.Object(id=server['id']) for server in SERVERS.values() if has_command('purge', server)])
async def purge(interaction: discord.Interaction):
    try:
        follow_up = interaction.channel.id
        await interaction.response.send_message(f"Working...")
        await interaction.channel.purge(limit=50)
        await client.get_channel(follow_up).send(f"Messages deleted! (Did I miss some? If I wasn't awake when it was sent, I cannot find it...)", delete_after=5)
    except discord.Forbidden:
        await interaction.response.send_message("Sorry, but you don't have the `Manage Messages` permission.", delete_after=10)
    except discord.HTTPException:
        await interaction.response.send_message("Sorry, I had an unexpected error. :/", delete_after=10)


@client.tree.command(name="archive",
                     description="Archives the CURRENT CHANNEL and creates a new one for the week!",
                     guilds=[discord.Object(id=server['id']) for server in SERVERS.values() if has_command('archive', server)])
@app_commands.describe(
    channel_name="What's the theme for this week?",
    nickname_for_isabella="Isabella's nickname!",
    nickname_for_carlos="Nickname for Carlos!"
)
async def archive(interaction: discord.Interaction, channel_name: str, nickname_for_isabella: str, nickname_for_carlos: str):
    data = SERVERS['Wine Moms']
    wendy: discord.CategoryChannel = interaction.guild.get_channel(data['channel_ids']['wendy'])
    archive_category: discord.CategoryChannel = interaction.guild.get_channel(data['channel_ids']['archive'])

    if interaction.channel not in wendy.channels:
        await interaction.response.send_message(f"Sorry, but this channel isn't in `{wendy.name}`. Please try a channel from that category instead!", ephemeral=True, delete_after=15)
        return

    await interaction.channel.move(category=archive_category, end=True) # moves to archive
    new_channel = await wendy.create_text_channel(channel_name) # creates new channel

    carlos = interaction.guild.get_member(data['user_ids']['carlos'])
    await interaction.guild.get_member(data['user_ids']['isabella']).edit(nick=nickname_for_isabella) # changes isabella nickname

    await new_channel.send(f"Welcome to the new theme for this week: {channel_name}! :sparkles:")
    await new_channel.send(f"I am not allowed to edit {carlos.mention}'s name, but his new nickname is `{nickname_for_carlos}`!")
    await new_channel.send("Have fun!! :orange_heart:")
    await interaction.response.send_message(f"Done! This channel is now archived. Please use {new_channel.mention} instead. Thank you! :orange_heart:")

client.run(os.getenv("DEV_BOT_TOKEN"))
