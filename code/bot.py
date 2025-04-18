import discord
from discord.ext import commands, tasks
import os
import requests
import lyricsgenius

import utils.config as config
from utils.command_tree import Tree
from utils.media_api_key import get_media_api_key


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="***",
            activity=discord.Game(name="music!"),
            intents=discord.Intents.default(),
            tree_cls=Tree,
        )

    async def setup_hook(self):
        # Get Spotify, Apple Music, and Genius access tokens/clients
        get_access_token.start()
        refresh_media_api_key.start()
        login_genius.start()
        config.LOG.info("Loading cogs...")
        if config.YOUTUBE_SUPPORT:
            config.LOG.info(
                "YouTube support is enabled, make sure to set a poToken"
            )
        else:
            config.LOG.warn("YouTube support is disabled")
        for ext in os.listdir("./code/cogs"):
            if ext.endswith(".py"):
                # Load the OPTIONAL feedback cog
                if (
                    ext[:-3] == "feedback"
                    and config.FEEDBACK_CHANNEL_ID == None
                ):
                    config.LOG.warn(
                        "Skipped loading feedback cog - channel ID not"
                        " provided"
                    )
                    continue
                # Load the OPTIONAL bug cog
                if ext[:-3] == "bug" and config.BUG_CHANNEL_ID == None:
                    config.LOG.warn(
                        "Skipped loading bug cog - channel ID not provided"
                    )
                    continue
                # Load the OPTIONAL lyrics cog
                if ext[:-3] == "lyrics" and config.GENIUS_CLIENT_ID == None:
                    config.LOG.warn(
                        "Skipped loading lyrics cog - Genius API credentials"
                        " not provided"
                    )
                    continue
                # Load the OPTIONAL autoplay cog
                if ext[:-3] == "autoplay" and config.AI_CLIENT == None:
                    config.LOG.warn(
                        "Skipped loading autoplay cog - AI API credentials"
                        " not provided"
                    )
                    continue

                await self.load_extension(f"cogs.{ext[:-3]}")
        for ext in os.listdir("./code/cogs/owner"):
            if ext.endswith(".py"):
                await self.load_extension(f"cogs.owner.{ext[:-3]}")

    async def on_ready(self):
        config.LOG.info(f"{bot.user} has connected to Discord.")
        config.LOG.info(
            "Startup complete. Sync slash commands by DMing the bot"
            f" {bot.command_prefix}tree sync (guild id)"
        )


bot = MyBot()
bot.remove_command("help")
bot.temp_command_count = {}  # command_name: count
bot.autoplay = []  # guild_id, guild_id, etc.
bot.youtube_broken = False


@tasks.loop(minutes=45)
async def get_access_token():
    if config.SPOTIFY_CLIENT_ID and config.SPOTIFY_CLIENT_SECRET:
        auth_url = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": config.SPOTIFY_CLIENT_ID,
            "client_secret": config.SPOTIFY_CLIENT_SECRET,
        }
        response = requests.post(auth_url, data=data)
        if response.status_code == 200:
            access_token = response.json()["access_token"]
            bot.spotify_headers = {"Authorization": f"Bearer {access_token}"}
    else:
        bot.spotify_headers = None


@tasks.loop(hours=24)
async def refresh_media_api_key():
    media_api_key = get_media_api_key()
    if media_api_key is not None:
        bot.apple_headers = {
            "Authorization": f"Bearer {media_api_key}",
            "Origin": "https://apple.com",
        }
    else:
        bot.apple_headers = None


@tasks.loop(hours=1)
async def login_genius():
    if config.GENIUS_CLIENT_ID and config.GENIUS_CLIENT_SECRET:
        auth_url = "https://api.genius.com/oauth/token"
        data = {
            "client_id": config.GENIUS_CLIENT_ID,
            "client_secret": config.GENIUS_CLIENT_SECRET,
            "grant_type": "client_credentials",
        }
        response = requests.post(auth_url, data=data)
        if response.status_code == 200:
            access_token = response.json()["access_token"]
            bot.genius = lyricsgenius.Genius(access_token)
            bot.genius.verbose = False
    else:
        bot.genius = None


if __name__ == "__main__":
    config.load_config()
    bot.run(config.TOKEN)
