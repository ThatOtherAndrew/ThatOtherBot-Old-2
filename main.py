import discord
from discord.ext import commands

import bot.settings as bot_settings
from bot.tools import log, settings, get_extensions


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
            log.info(f'Copied global slash commands to guild ID {settings["debug_guild_id"]}')

        log.info(f'Logged in as {bot.user}')

    async def add_cog(self, cog: commands.Cog, *, settings_template: bot_settings.settings_template = None, **kwargs):
        table_name = cog.__class__.__name__.lower()

        if settings_template is not None:
            if table_name in settings:
                table = settings[table_name]
            else:
                log.info(f'Table "{table_name}" in configuration file missing, generating from template')
                table = bot_settings.generate(settings_template, table=True)

            settings[table_name] = bot_settings.validate(table, settings_template)
            bot_settings.save(settings, 'settings.toml')

        await super().add_cog(cog, **kwargs)

    def run(self, token: str, *args, **kwargs):
        if not token:
            raise ValueError('Bot token is not specified')

        super().run(token, *args, **kwargs)


bot = Bot(command_prefix='!', intents=discord.Intents.all())


@bot.tree.command()
async def test(interaction: discord.Interaction):
    await interaction.response.send_message(settings['core']['test_message'])


if __name__ == '__main__':
    bot.run(settings['bot_token'])
