import logging
import sys

import discord
from discord.ext import commands
from discord import app_commands


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(name)s: %(message)s')
        file_handler = logging.FileHandler('logs/discord.log', 'w', 'utf-8')
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))


bot = Bot(command_prefix='!', intents=discord.Intents.all())
tree = app_commands.CommandTree(bot)


@bot.event
async def on_ready():
    bot.logger.info(f'Logged in as {bot.user}')


if __name__ == '__main__':
    bot.run(input('Token: '))
