from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from bot.settings import Option

if TYPE_CHECKING:
    from main import Bot


settings = [
    Option('test_message', 'Received!'),
]


class Core(commands.Cog):
    def __init__(self, bot: 'Bot'):
        self.bot = bot

    @commands.command()
    async def sync(self, ctx: commands.Context):
        await self.bot.tree.sync(guild=discord.Object(id=ctx.guild.id))
        await ctx.reply('Synchronised the bot command tree.')


async def setup(bot: 'Bot'):
    await bot.add_cog(Core(bot), settings_template=settings)
