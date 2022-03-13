import logging

import discord
from discord.ext import commands
from discord import app_commands

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
tree = app_commands.CommandTree(bot)


@bot.event
async def on_ready():
    bot.logger.info(f'Logged in as {bot.user}')


if __name__ == '__main__':
    for extension in get_extensions('bot/extensions'):
        try:
            bot.load_extension(extension)
            bot.logger.info(f'Extension loaded: {extension}')
        except Exception as extension_error:
            bot.logger.error(extension_error)

    bot.run(input())
