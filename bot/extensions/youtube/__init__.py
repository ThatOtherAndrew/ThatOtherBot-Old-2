from pathlib import Path
from typing import TYPE_CHECKING

import discord
from discord.ext.commands import Cog
import youtubesearchpython.__future__ as yt

if TYPE_CHECKING:
    from main import Bot


root = Path(__file__).parent


class YouTube(Cog):
    def __init__(self, bot: 'Bot'):
        self.bot = bot

    @discord.app_commands.command()
    async def youtube(self, interaction: discord.Interaction, search_query: str):
        """Search YouTube for a video and get the top result."""
        results = await yt.VideosSearch(search_query, limit=1).next()

        if results['result']:
            await interaction.response.send_message(f'https://youtu.be/{results["result"][0]["id"]}')
        else:
            embed = discord.Embed(
                title='No YouTube search results found',
                description='Try rewording your query, or try again later if there are still no results found.',
                colour=0xFF0000
            )
            icon = discord.File(root/'search.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            await interaction.response.send_message(embed=embed, file=icon, ephemeral=True)


async def setup(bot: 'Bot'):
    await bot.add_cog(YouTube(bot))
