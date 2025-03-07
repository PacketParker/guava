import discord
import datetime
from discord import app_commands
from discord.ext import commands
from cogs.music import Music
import asyncio

from utils.config import create_embed
from utils.custom_sources import LoadError


class Skip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.check(Music.create_player)
    @app_commands.describe(
        number="Optional: Number of songs to skip, default is 1"
    )
    async def skip(self, interaction: discord.Interaction, number: int = 1):
        "Skips the song that is currently playing"
        player = self.bot.lavalink.player_manager.get(interaction.guild.id)

        if number != 1:
            if number < 1:
                embed = create_embed(
                    title="Invalid Number",
                    description="The number option cannot be less than 1",
                )
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )

            elif number > len(player.queue):
                embed = create_embed(
                    title="Number too Large",
                    description=(
                        "The number you entered is larger than the number of"
                        " songs in queue. If you want to stop playing music"
                        " entirely, try the </stop:1224840890866991305>"
                        " command."
                    ),
                )
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )
            else:
                for i in range(number - 2, -1, -1):
                    player.queue.pop(i)

        # If the queue is empty, but the current song is on repeat
        if player.loop == 1 and not player.queue:
            embed = create_embed(
                title="Song on Repeat",
                description=(
                    "There is nothing in queue, but the current song is on"
                    " repeat. Use </stop:1224840890866991305> to stop"
                    " playing music."
                ),
            )
            return await interaction.response.send_message(
                embed=embed, ephemeral=True
            )
        else:
            pass

        # Skip current track, continue skipping on LoadError
        while True:
            try:
                await player.skip()
                break
            except LoadError as e:
                continue

        if not player.current:
            embed = create_embed(
                title="End of Queue",
                description=(
                    "I have left the voice channel as all songs in the queue"
                    " have been played.\n\n"
                    f"Issued by: {interaction.user.mention}"
                ),
            )
            return await interaction.response.send_message(embed=embed)

        # It takes a sec for the new track to be grabbed and played
        # So just wait a sec before sending the message
        await asyncio.sleep(0.5)
        embed = create_embed(
            title=(
                f"{'Track Skipped' if number == 1 else f'{number} Tracks Skipped'}"
            ),
            description=(
                f"**[{player.current.title}]({player.current.uri})**"
                f" by **{player.current.author}** is now playing\n\n"
                f"Issued by: {interaction.user.mention}"
            ),
            thumbnail=player.current.artwork_url,
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Skip(bot))
