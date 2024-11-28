import discord
import datetime
from discord import app_commands
from discord.ext import commands
from cogs.music import Music
from typing import Literal

from utils.ai_recommendations import add_song_recommendations
from utils.config import create_embed


class Autoplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.check(Music.create_player)
    @app_commands.describe(toggle="Turn autoplay ON or OFF")
    async def autoplay(
        self, interaction: discord.Interaction, toggle: Literal["ON", "OFF"]
    ):
        "Keep the music playing forever with music suggestions from OpenAI"
        if toggle == "OFF":
            self.bot.autoplay.remove(interaction.guild.id)

            embed = create_embed(
                title="Autoplay Off",
                description=(
                    "Autoplay has been turned off. I will no longer"
                    " automatically add new songs to the queue based on AI"
                    " recommendations."
                ),
            )
            return await interaction.response.send_message(embed=embed)

        # Otherwise, toggle must be "ON", so enable autoplaying

        if interaction.guild.id in self.bot.autoplay:
            embed = create_embed(
                title="Autoplay Already Enabled",
                description=(
                    "Autoplay is already enabled. If you would like to turn it"
                    " off, choose the `OFF` option in the"
                    " </autoplay:1228216490386391052> command."
                ),
            )
            return await interaction.response.send_message(
                embed=embed, ephemeral=True
            )

        player = self.bot.lavalink.player_manager.get(interaction.guild.id)

        if len(player.queue) < 5:
            embed = create_embed(
                title="Not Enough Context",
                description=(
                    "You must have at least 5 songs in the queue so that I can"
                    " get a good understanding of what music I should continue"
                    " to play. Add some more music to the queue, then try"
                    " again."
                ),
            )
            return await interaction.response.send_message(
                embed=embed, ephemeral=True
            )

        inputs = {}
        for song in player.queue[:10]:
            inputs[song.title] = song.author

        embed = create_embed(
            title="Getting AI Recommendations",
            description=(
                "Attempting to generate recommendations based on the current"
                " songs in your queue. Just a moment..."
            ),
        )
        await interaction.response.send_message(embed=embed)

        if await add_song_recommendations(
            self.bot.openai, self.bot.user, player, 5, inputs
        ):
            self.bot.autoplay.append(interaction.guild.id)
            embed = create_embed(
                title=":infinity: Autoplay Enabled :infinity:",
                description=(
                    "I have added a few similar songs to the queue and will"
                    " continue to do so once the queue gets low again. Now"
                    " just sit back and enjoy the music!\n\nEnabled by:"
                    f" {interaction.user.mention}"
                ),
            )
            await interaction.edit_original_response(embed=embed)

        else:
            embed = create_embed(
                title="Autoplay Error",
                description=(
                    "Autoplay is an experimental feature, meaning sometimes it"
                    " doesn't work as expected. I had an error when attempting"
                    " to get similar songs for you, please try running the"
                    " command again. If the issue persists, fill out a bug"
                    " report with the </bug:1224840889906499626> command."
                ),
            )
            await interaction.edit_original_response(embed=embed)


async def setup(bot):
    await bot.add_cog(Autoplay(bot))
