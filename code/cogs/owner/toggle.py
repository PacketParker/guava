from discord.ext import commands
from typing import Literal


class Toggle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.dm_only()
    @commands.is_owner()
    async def toggle(self, ctx, action: Literal["on", "off"]):
        """Toggle YouTube as broken or not"""
        if action == "on":
            self.bot.youtube_broken = False
            return await ctx.send("YouTube has been enabled.")

        if action == "off":
            self.bot.youtube_broken = True
            return await ctx.send("YouTube has been marked as broken.")

    @toggle.error
    async def toggle_error(self, ctx, error):
        if isinstance(error, commands.BadLiteralArgument):
            return await ctx.send("Invalid action. Use either 'on' or 'off'.")
        else:
            return await ctx.send("An unknown error occurred.")


async def setup(bot):
    await bot.add_cog(Toggle(bot))
