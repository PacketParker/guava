from discord.ext import commands
from typing import Literal

import utils.config as config


class Toggle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.dm_only()
    @commands.is_owner()
    async def toggle(
        self, ctx, action: Literal["disable", "enable", "broken"]
    ):
        """Toggle YouTube links"""
        if action == "disable":
            config.YOUTUBE_SUPPORT = False
            config.YOUTUBE_BROKEN = False
            return await ctx.send("YouTube has been disabled.")

        if action == "enable":
            config.YOUTUBE_SUPPORT = True
            config.YOUTUBE_BROKEN = False
            return await ctx.send("YouTube has been enabled.")

        if action == "broken":
            config.YOUTUBE_SUPPORT = False
            config.YOUTUBE_BROKEN = True
            return await ctx.send("YouTube has been marked as broken.")


async def setup(bot):
    await bot.add_cog(Toggle(bot))
