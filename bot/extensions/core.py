from discord.ext import commands

from main import Bot


class Core(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx: commands.Context):
        await ctx.reply('Received!')


def setup(bot: Bot):
    bot.add_cog(Core(bot))
