import discord
from discord.ext import commands

from main import Bot


class Core(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx: commands.Context):
        await ctx.reply('Received!')

    @commands.command()
    async def sync(self, ctx: commands.Context):
        await self.bot.tree.sync(guild=discord.Object(id=824577786496417844))
        await ctx.reply('Synchronised the bot command tree.')


def setup(bot: Bot):
    bot.add_cog(Core(bot))
