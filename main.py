import discord
from discord.ext import commands

import bot.settings as bot_settings
from bot.settings import settings
from bot.tools import log, get_extensions


class Bot(commands.Bot):
    async def setup_hook(self):
        for extension in get_extensions('bot/extensions'):
            try:
                await bot.load_extension(extension)
                log.info(f'Extension loaded: {extension.removeprefix("bot.extensions.")}')
            except Exception as extension_error:
                log.error(extension_error)

        if settings['debug_mode']:
            self.tree.copy_global_to(guild=discord.Object(id=settings['debug_guild_id']))
            log.debug(f'Copied global slash commands to guild ID {settings["debug_guild_id"]}')

        log.info(f'Logged in as {bot.user}')

    async def add_cog(self, cog: commands.Cog, *, settings_template: bot_settings.settings_template = None, **kwargs):
        if settings_template is not None:
            bot_settings.add_table(cog.__class__.__name__, settings_template)

        await super().add_cog(cog, **kwargs)

    def run(self, token: str, *args, **kwargs):
        if not token:
            raise ValueError('Bot token is not specified')

        super().run(token, *args, **kwargs)


bot = Bot(command_prefix='!', intents=discord.Intents.all())


if __name__ == '__main__':
    if settings['debug_mode']:
        if settings['logging_level'] == 3:
            log.debug('Debug mode is enabled')
        else:
            log.warning(f'Debug mode is enabled, but current logging level is set to {settings["logging_level"]}')

    bot.run(settings['bot_token'])
