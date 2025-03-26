from discord.ext import commands
from typing import Literal

from utils.config import YOUTUBE_SUPPORT, YOUTUBE_BROKEN


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
            YOUTUBE_SUPPORT = False
            YOUTUBE_BROKEN = False
            return await ctx.send("YouTube has been disabled.")

        if action == "enable":
            YOUTUBE_SUPPORT = True
            YOUTUBE_BROKEN = False
            return await ctx.send("YouTube has been enabled.")

        if action == "broken":
            YOUTUBE_SUPPORT = False
            YOUTUBE_BROKEN = True
            return await ctx.send("YouTube has been marked as broken.")


async def setup(bot):
    await bot.add_cog(Toggle(bot))
