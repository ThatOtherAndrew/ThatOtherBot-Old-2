import json
from pathlib import Path
from typing import TYPE_CHECKING, AsyncGenerator

import discord
from discord.ext.commands import Cog

if TYPE_CHECKING:
    from main import Bot

root = Path(__file__).parent


async def bookmark_fetcher(client: discord.Client, pages: list[list[int]]) -> AsyncGenerator[tuple[str, str], None]:
    """Resolves bookmark contents and author from message and channel IDs"""
    for bookmark in pages:
        message = await client.get_channel(bookmark[0]).fetch_message(bookmark[1])
        text = discord.utils.remove_markdown(message.content).rstrip(']') or '<Empty>'

        if len(text) > 512:
            text = f'{text[:509]}...'
        if (count := text.count('\n')) > 15:
            text = '\n'.join(text.split('\n', 15)[:15]) + f'\n*({count - 15} more line{"s" if count != 16 else ""})*'

        yield (
            discord.utils.escape_markdown(message.author.display_name),
            f'[{text}](https://discord.com/channels/{message.guild.id}/{bookmark[0]}/{bookmark[1]})'
        )


async def render_bookmarks(interaction: discord.Interaction, view: 'NavigationButtons' = None,
                           *, pages: list[list[list[int]]], index: int) -> None:
    """Renders bookmarks into a paginated embed message"""
    embed = discord.Embed(
        title='🔖 Your Bookmarks',
        description=f'Page {index + 1} of {len(pages)}',
        colour=discord.Colour.blurple()
    )
    for content in pages[index]:
        embed.add_field(
            name='Loading preview...',
            value='[Link to message]'
                  f'(https://discord.com/channels/{interaction.guild.id}/{content[0]}/{content[1]})',
            inline=False
        )
    if view is None:
        await interaction.response.send_message(embed=embed, view=NavigationButtons(pages=pages, index=index))
    else:
        await interaction.message.edit(embed=embed, view=view)
        await interaction.response.defer()

    embed.clear_fields()
    async for content in bookmark_fetcher(interaction.client, pages[index]):
        embed.add_field(name=content[0], value=content[1], inline=False)
    if view is None:
        await interaction.edit_original_message(embed=embed)
    else:
        await interaction.message.edit(embed=embed)


class NavigationButtons(discord.ui.View):
    def __init__(self, pages: list[list[list[int]]], index: int):
        super().__init__()
        self.pages = pages
        self.index = index
        self.update_buttons()

    def update_buttons(self):
        discord.utils.get(self.children, custom_id='bookmarks:previous_page').disabled = self.index <= 0
        discord.utils.get(self.children, custom_id='bookmarks:next_page').disabled = self.index >= len(self.pages) - 1

    @discord.ui.button(label='Previous Page', style=discord.ButtonStyle.blurple,
                       emoji='⬅', custom_id='bookmarks:previous_page')
    async def previous_page(self, interaction: discord.Interaction, _):
        self.index -= 1
        self.update_buttons()
        await render_bookmarks(interaction, self, pages=self.pages, index=self.index)

    @discord.ui.button(label='Next Page', style=discord.ButtonStyle.blurple, emoji='➡', custom_id='bookmarks:next_page')
    async def next_page(self, interaction: discord.Interaction, _):
        self.index += 1
        self.update_buttons()
        await render_bookmarks(interaction, self, pages=self.pages, index=self.index)


class Bookmarks(Cog):
    def __init__(self, bot: 'Bot'):
        self.bot = bot
        if (root/'bookmarks.json').exists():
            with (root/'bookmarks.json').open('r') as f:
                self.bookmarks: dict[str, list[list[int]]] = json.load(f)
        else:
            self.bookmarks: dict[str, list[list[int]]] = {}
        self.bookmark_message = self.create_bookmark_message()
        self.bot.tree.add_command(self.bookmark_message)

    # Context menu commands are not supported in cogs, so this jank will have to stay for now
    def create_bookmark_message(self) -> discord.app_commands.ContextMenu:
        @discord.app_commands.context_menu(name='Bookmark Message')
        async def bookmark(interaction: discord.Interaction, message: discord.Message):
            """Bookmarks the selected message to easily refer to later."""
            key = str(interaction.user.id)
            if key not in self.bookmarks:
                self.bookmarks[key] = []
            if message.id in self.bookmarks[key]:
                await interaction.response.send_message('This message has already been bookmarked!', ephemeral=True)
                return

            self.bookmarks[key].insert(0, [message.channel.id, message.id])
            with (root/'bookmarks.json').open('w') as f:
                json.dump(self.bookmarks, f, indent=2)

            embed = discord.Embed(
                title='Message bookmarked!',
                description='Use the `/bookmarks` command to view all your bookmarks.',
                colour=discord.Colour.green()
            )
            embed.set_footer(
                text=f'{message.author.display_name}\'s message',
                icon_url=message.author.display_avatar.url
            )
            if message.content:
                embed.add_field(
                    name='Message text',
                    value=message.content if len(message.content) <= 1024 else message.content[:1021] + '...',
                    inline=False
                )
            if message.attachments:
                embed.add_field(
                    name='Attachments',
                    value='\n'.join(
                        f'`{att.filename}` '
                        f'({att.content_type.split("/")[0].capitalize()} file, '
                        f'{att.content_type.split("/")[1].upper()} format)'
                        for att in message.attachments
                    ),
                    inline=False
                )
            if image := discord.utils.find(lambda att: att.content_type.startswith('image/'), message.attachments):
                embed.set_image(url=image.url)

            view = discord.ui.View()
            view.add_item(discord.ui.Button(
                label='Link to bookmarked message',
                url=f'https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}'
            ))

            await interaction.response.send_message(embed=embed, view=view)

        return bookmark

    @discord.app_commands.command(name='bookmarks')
    async def get_bookmarks(self, interaction: discord.Interaction, page: int = 1):
        """Fetch all the bookmarks you've saved in this server."""
        key = str(interaction.user.id)
        pages = [self.bookmarks[key][i:i+5] for i in range(0, len(self.bookmarks[key]) + 1, 5)]
        page = min(page, len(pages)) - 1

        await render_bookmarks(interaction, pages=pages, index=page)


async def setup(bot: 'Bot'):
    await bot.add_cog(Bookmarks(bot))
