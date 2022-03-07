import logging
import sys

import discord
from discord.ext import commands
from discord import app_commands

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
logger_file_handler = logging.FileHandler('logs/discord.log', 'w', 'utf-8')
logger_file_handler.setFormatter(logging.Formatter('[%(asctime)s %(levelname)s] %(name)s: %(message)s'))
logger_stream_handler = logging.StreamHandler(sys.stdout)
logger_stream_handler.setFormatter(logging.Formatter('[%(levelname)s] %(name)s: %(message)s'))
logger.addHandler(logger_file_handler)
logger.addHandler(logging.StreamHandler(sys.stdout))

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
tree = app_commands.CommandTree(bot)


@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')


@bot.command()
async def test(ctx: commands.Context):
    await ctx.reply('Received!')


if __name__ == '__main__':
    bot.run(input('Token: '))
