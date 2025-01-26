from discord.ext import commands


class Send(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.dm_only()
    @commands.is_owner()
    async def send(self, ctx, user_id: int, message: str):
        """Send a message to a user (follow-up on bug reports)"""
        user = self.bot.get_user(user_id)

        if not user:
            return await ctx.send("User not found.")

        elif not message:
            return await ctx.send("No message for user.")

        try:
            await user.send(message)
        except Exception as e:
            await ctx.send("Error sending message to user.")


async def setup(bot):
    await bot.add_cog(Send(bot))
