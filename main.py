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

    async def setup_hook(self):
        for extension in get_extensions('bot/extensions'):
            try:
                await bot.load_extension(extension)
                bot.logger.info(f'Extension loaded: {extension}')
            except Exception as extension_error:
                bot.logger.error(extension_error)

        bot.logger.info(f'Logged in as {bot.user}')


bot = Bot(command_prefix='!', intents=discord.Intents.all())


@bot.tree.command()
async def test(interaction: discord.Interaction):
    await interaction.response.send_message('Received!', ephemeral=True)


if __name__ == '__main__':
    bot.run(input())
