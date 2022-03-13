import logging

import discord
from discord.ext import commands

from bot.tools import get_extensions


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(name)s: %(message)s')
        handler = logging.FileHandler('logs/discord.log', 'w', 'utf-8')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)


bot = Bot(command_prefix='!', intents=discord.Intents.all())


@bot.event
async def on_ready():
    bot.logger.info(f'Logged in as {bot.user}')


@bot.tree.command(guild=discord.Object(id=824577786496417844))
async def test(interaction: discord.Interaction):
    await interaction.response.send_message('Received!', ephemeral=True)


if __name__ == '__main__':
    for extension in get_extensions('bot/extensions'):
        try:
            bot.load_extension(extension)
            bot.logger.info(f'Extension loaded: {extension}')
        except Exception as extension_error:
            bot.logger.error(extension_error)

    bot.run(input())
