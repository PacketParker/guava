import discord
from discord import app_commands
from discord.ext.commands.errors import *
import datetime

from cogs.music import CheckPlayerError
from config import BOT_COLOR
from custom_source import LoadError


class Tree(app_commands.CommandTree):
    async def on_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        music_commands = [
            "play",
            "clear",
            "np",
            "pause",
            "queue",
            "remove",
            "resume",
            "shuffle",
            "skip",
            "stop",
        ]

        if isinstance(error, CommandNotFound):
            return

        # Custom Error class for the `create_player` function
        # Issues that arise may be user not in vc, user not in correct vc, missing perms, etc.
        elif isinstance(error, CheckPlayerError):
            embed = discord.Embed(
                title=error.info["title"],
                description=error.info["description"],
                color=BOT_COLOR,
            )
            embed.set_footer(
                text=datetime.datetime.now(datetime.timezone.utc).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                + " UTC"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        # If `create_player` fails to create a player and fails
        # to raise a `CheckPlayerError`, this will catch it
        elif (
            isinstance(error, app_commands.CheckFailure)
            and interaction.command.name in music_commands
        ):
            embed = discord.Embed(
                title="Player Creation Error",
                description="An error occured when creating a player. Please try again.",
                color=BOT_COLOR,
            )
            embed.set_footer(
                text=datetime.datetime.now(datetime.timezone.utc).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                + " UTC"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        # If a Spotify song is linked but cannot be found on a provider (e.g. YouTube)
        elif isinstance(error, LoadError):
            embed = discord.Embed(
                title="Nothing Found",
                description="Spotify does not allow direct play, meaning songs have to be found on a supported provider. In this case, the song couldn't be found. Please try again with a different song, or try searching for just the name and artist manually rather than sending a link.",
                color=BOT_COLOR,
            )
            embed.set_footer(
                text=datetime.datetime.now(datetime.timezone.utc).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                + " UTC"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        else:
            raise error#
