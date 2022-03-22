import discord
from discord.ext import commands

from bot import settings
from bot.tools import log, get_extensions


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.settings = settings.load('settings.toml')

        super().__init__(*args, **kwargs)

    async def setup_hook(self):
        for extension in get_extensions('bot/extensions'):
            try:
                await bot.load_extension(extension)
                log.info(f'Extension loaded: {extension}')
            except Exception as extension_error:
                log.error(extension_error)

        log.info(f'Logged in as {bot.user}')

    async def add_cog(self, cog: commands.Cog, /, *, settings_template: settings.settings_template = None, **kwargs):
        await super().add_cog(cog, **kwargs)


bot = Bot(command_prefix='!', intents=discord.Intents.all())


@bot.tree.command()
async def test(interaction: discord.Interaction):
    await interaction.response.send_message('Received!')


if __name__ == '__main__':
    bot.run(input())
