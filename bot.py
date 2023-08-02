import discord
import datetime
from discord import app_commands
from spotify_tools import SpotifyCache, get_spotify_activity
from data_tools import JSONData

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True


DATA = JSONData(prod=True)


class ChaluBot(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

        self._SPOTIFY_CACHE = SpotifyCache()

    async def on_ready(self):
        self._SPOTIFY_CACHE.old_cache()

        await self.change_presence(status=discord.Status.online, activity=discord.Game("with my food"))
        print("Ready to go!")
        if DATA.in_beta():
            print("BETA WARNING: This is in development mode. Only ChaluBot Developer server data is available.")

    async def on_presence_update(self, _, after: discord.Member):
        activity = get_spotify_activity(after)
        if not activity:
            return
        
        spotify_servers = DATA.get_server_data(with_feature="spotify")
        if after.guild.id in spotify_servers.keys() and not self._SPOTIFY_CACHE.in_cache(activity.track_id, after.id):
            self._SPOTIFY_CACHE.add_to_cache(activity, after)

            [await self.get_channel(server_data['channel_ids']['spotify']).send("", embeds=[SpotifyCache.build_embed(activity, after, client)]) for guild_id, server_data in spotify_servers.items() if after in self.get_guild(guild_id).members]

    async def setup_hook(self):
        for guild_id, server_data in DATA.get_server_data(with_feature='commands').items():
            print(f"Updated {server_data['nick']} commands.")
            await self.tree.sync(guild=discord.Object(id=guild_id))


# Commands begin below.
client = ChaluBot(intents=intents)


def has_command(command_name: str, server_data: dict) -> bool:
    return server_data['features']['commands'] and command_name in server_data['features']['commands']


@client.tree.command(name="purge",
                     description="A classic purge command! 50 messages at a time.",
                     guilds=[discord.Object(id=guild_id) for guild_id in DATA.get_server_data(with_feature='commands:purge').keys()])
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
                     guilds=[discord.Object(id=guild_id) for guild_id in DATA.get_server_data(with_feature='commands:archive').keys()])
@app_commands.describe(
    channel_name="What's the theme for this week?",
    nickname_for_isabella="Isabella's nickname!",
    nickname_for_carlos="Nickname for Carlos!"
)
async def archive(interaction: discord.Interaction, channel_name: str, nickname_for_isabella: str, nickname_for_carlos: str):
    server_data = DATA.get_server_data(1131973022207725660)
    wendy: discord.CategoryChannel = interaction.guild.get_channel(server_data['channel_ids']['wendy'])
    archive_category: discord.CategoryChannel = interaction.guild.get_channel(server_data['channel_ids']['archive'])

    if interaction.channel not in wendy.channels:
        await interaction.response.send_message(f"Sorry, but this channel isn't in `{wendy.name}`. Please try a channel from that category instead!", ephemeral=True, delete_after=15)
        return

    await interaction.channel.move(category=archive_category, end=True) # moves to archive
    new_channel = await wendy.create_text_channel(channel_name) # creates new channel

    carlos = interaction.guild.get_member(server_data['user_ids']['carlos'])
    await interaction.guild.get_member(server_data['user_ids']['isabella']).edit(nick=nickname_for_isabella) # changes isabella nickname

    await new_channel.send(f"Welcome to the new theme for this week: {channel_name}! :sparkles:")
    await new_channel.send(f"I am not allowed to edit {carlos.mention}'s name, but his new nickname is `{nickname_for_carlos}`!")
    await new_channel.send("Have fun!! :orange_heart:")
    await interaction.response.send_message(f"Done! This channel is now archived. Please use {new_channel.mention} instead. Thank you! :orange_heart:")


@client.tree.command(name="set",
                     description="Set the event for Game Night! Only Carlos or Joseph can activate this.",
                     guilds=[discord.Object(id=guild_id) for guild_id in DATA.get_server_data(with_feature='commands:set').keys()])
async def set(interaction: discord.Interaction):
    guild_id, server_data = DATA.get_server_data(1134495510573621338).items()

    if interaction.user.id not in (890992783689670679, 458773298961055758):
        await interaction.response.send_message("Sorry, you cannot use this command. Only Carlos or Joseph can use it.", ephemeral=True)

    dt = datetime.datetime.today()
    
    while dt.weekday() != 4:
        dt = dt + datetime.timedelta(days=1.0)

    event = await client.get_guild(guild_id).create_scheduled_event(
            name="Game Night",
            description="Join us in our (not so weekly) game night!",
            location=server_data['event_location'],
            start_time=datetime.datetime(year=dt.year, month=dt.month, day=dt.day+1, hour=3, tzinfo=datetime.UTC),
            end_time=datetime.datetime(dt.year, dt.month, dt.day+1, hour=7, tzinfo=datetime.UTC),
            entity_type=discord.EntityType.external,
            privacy_level=discord.PrivacyLevel.guild_only
        )
    
    await interaction.response.send_message(f"`{event.name}` has been created and scheduled for `{event.start_time.month}/{event.start_time.day-1}/{event.start_time.year}`!")
    

client.run(DATA.get_token())
