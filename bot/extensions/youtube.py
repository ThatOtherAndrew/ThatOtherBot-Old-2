from typing import TYPE_CHECKING

import discord
from discord.ext.commands import Cog
import youtubesearchpython.__future__ as yt

from bot.settings import Option

if TYPE_CHECKING:
    from main import Bot


settings = [
    Option('key', 'value'),
]


class YouTube(Cog):
    def __init__(self, bot: 'Bot'):
        self.bot = bot

    @discord.app_commands.command()
    async def youtube(self, interaction: discord.Interaction, search_query: str):
        results = await yt.VideosSearch(search_query, limit=1).next()

        if results['result']:
            await interaction.response.send_message(f'https://youtu.be/{results["result"][0]["id"]}')
        else:
            embed = discord.Embed(
                title='No YouTube search results found',
                description='Try rewording your query',
                color=0xFF0000
            )
            icon = discord.File('assets/img/e.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            await interaction.response.send_message(embed=embed, file=icon, ephemeral=True)


async def setup(bot: 'Bot'):
    await bot.add_cog(YouTube(bot), settings_template=settings)
