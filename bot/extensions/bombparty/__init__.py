import asyncio
import random
from itertools import islice
from pathlib import Path
from typing import TYPE_CHECKING

import discord
from discord.ext.commands import Cog

from bot.settings import settings, Option

if TYPE_CHECKING:
    from main import Bot

root = Path(__file__).parent
settings_template = [
    Option('bomb_timer', 8, enforce_type=False, validator=lambda value: isinstance(value, (int, float)))
]


class Lobby(discord.ui.View):
    def __init__(self, message: discord.Message, thread: discord.Thread, leader: discord.Member):
        super().__init__(timeout=None)
        self.message = message
        self.thread = thread
        self.leader = leader
        self.players = [leader]
        self.ready = False

    @discord.ui.button(label='Join Game', style=discord.ButtonStyle.blurple, emoji='⤵', custom_id='bombparty:join_game')
    async def join_game(self, interaction: discord.Interaction, _):
        if interaction.user in self.players:
            await interaction.response.send_message('You\'ve already joined the game!', ephemeral=True)
            return

        self.players.append(interaction.user)
        await self.thread.send(f'> ⤵ {interaction.user.mention} joined the game.')

        embed = interaction.message.embeds[0]
        embed.title = f'BombParty Game Lobby ({len(self.players)})'
        if len(self.players) > 1:
            discord.utils.get(self.children, custom_id='bombparty:start_game').disabled = False
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='Leave Game', style=discord.ButtonStyle.grey, emoji='⤴', custom_id='bombparty:leave_game')
    async def leave_game(self, interaction: discord.Interaction, _):
        if interaction.user not in self.players:
            await interaction.response.send_message('You\'re not in the game!', ephemeral=True)
            return

        self.players.remove(interaction.user)

        if len(self.players) == 0:
            await self.thread.send(
                f'> ⤴ {interaction.user.mention}, the last player, left the game.\n> 🔒 Lobby closed.',
                allowed_mentions=discord.AllowedMentions.none()
            )
            embed = discord.Embed(title='BombParty Game Ended', description='All players have left this game.')
            await interaction.response.edit_message(embed=embed, view=None)
            self.stop()

        else:
            embed = interaction.message.embeds[0]
            embed.title = f'BombParty Game Lobby ({len(self.players)})'

            if interaction.user == self.leader:
                self.leader = self.players[0]
                await self.thread.send(
                    f'> ⤴ {interaction.user.mention}, the game leader, left the game.\n'
                    f'> 👑 {self.leader.mention} has been automatically promoted to game leader.',
                    allowed_mentions=discord.AllowedMentions(users=[self.leader])
                )
                embed.set_footer(
                    text=f'{self.leader.display_name} is the current game leader.',
                    icon_url=self.leader.display_avatar.url
                )
            else:
                await self.thread.send(
                    f'> ⤴ {interaction.user.mention} left the game.',
                    allowed_mentions=discord.AllowedMentions.none()
                )
            if len(self.players) == 1:
                discord.utils.get(self.children, custom_id='bombparty:start_game').disabled = True
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='Start Game', style=discord.ButtonStyle.green, emoji='▶',
                       disabled=True, custom_id='bombparty:start_game')
    async def start_game(self, interaction: discord.Interaction, _):
        if interaction.user != self.leader:
            await interaction.response.send_message('You\'re not the game leader!', ephemeral=True)
            return

        embed = discord.Embed(
            title='BombParty Game in Progress',
            description=f'{len(self.players)} player{" is" if len(self.players) == 1 else "s are"} currently playing.',
            colour=0x3AA35B
        )
        embed.set_footer(
            text=f'{self.leader.display_name} is the current game leader.',
            icon_url=self.leader.display_avatar.url
        )
        for button in self.children:
            button.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)
        await self.thread.send('> 🚪 **Lobby has closed.**')
        self.ready = True
        self.stop()


class Game:
    def __init__(self, bot: 'Bot', thread: discord.Thread, players: list[discord.Member], words: set[str]):
        self.bot = bot
        self.thread = thread
        self.players = random.sample(players, len(players))
        self.words = words
        self.used_words = []
        self.playing = True
        self.prompt = None

    async def play(self, lobby: Lobby) -> None:
        self.prompt = self.generate_prompt()

        while self.playing:
            current_player = self.players.pop(0)
            await self.thread.send(f'> 🧨 {current_player.mention}: **{self.prompt}**')

            try:
                guess: discord.Message = await self.bot.wait_for(
                    'message',
                    check=lambda message: message.author == current_player and self.check_guess(message.content),
                    timeout=float(settings['bombparty']['bomb_timer'])
                )
            except asyncio.TimeoutError:
                await self.thread.send(f'> 💥 {current_player.mention} was too slow and exploded!')
            else:
                await self.thread.send(f'> ✅ `{guess.content}` is correct!')
                self.players.append(current_player)
                self.prompt = self.generate_prompt()

            if len(self.players) == 1:
                await self.thread.send(f'> 🏆 {self.players[0].mention} is the winner!')
                self.playing = False

        embed = discord.Embed(title='BombParty Game Ended', description='This game of BombParty is no longer active.')
        await lobby.message.edit(embed=embed, view=None)
        await lobby.thread.edit(locked=True)

    def generate_prompt(self) -> str:
        index = random.randrange(len(self.words))
        word = next(islice(self.words, index, index + 1))

        index = random.randrange(len(word) - 1)
        if len(word[index:]) >= 3 and random.random() > 0.7:
            return word[index:index+3]
        return word[index:index+2]

    def check_guess(self, message: str) -> bool:
        guess = message.lower()

        if guess.isalpha() and self.prompt in guess and guess not in self.used_words and guess in self.words:
            self.used_words.append(guess)
            return True
        else:
            return False


class BombParty(Cog):
    def __init__(self, bot: 'Bot'):
        self.bot = bot
        with (root/'wordlist.txt').open('r') as f:
            self.words = set(f.read().split())

    @discord.app_commands.command()
    async def bombparty(self, interaction: discord.Interaction):
        """Start a game of BombParty to play with your friends!"""
        await interaction.response.send_message(embed=discord.Embed(title='Loading, please wait...'))
        message = await interaction.original_message()
        thread = await message.create_thread(name='BombParty', auto_archive_duration=60)
        lobby = Lobby(message, thread, interaction.user)

        embed = discord.Embed(
            title=f'BombParty Game Lobby ({len(lobby.players)})',
            description='Join the game with the buttons below!',
            colour=0x5865F2
        )
        embed.set_footer(
            text=f'{interaction.user.display_name} is the current game leader.',
            icon_url=interaction.user.display_avatar.url
        )
        await thread.send(f'> 👑 {interaction.user.mention} is the game leader.')
        await message.edit(embed=embed, view=lobby)
        await lobby.wait()
        if not lobby.ready:
            raise TimeoutError('Interaction ended without ready condition being met')

        await asyncio.sleep(2)
        for i in range(3, 0, -1):
            await thread.send(f'> ⏳ Starting in {i}...')
            await asyncio.sleep(1)
        await thread.send('> 🏁 **Game has started!**')

        game = Game(self.bot, thread, lobby.players, self.words)
        await game.play(lobby)


async def setup(bot: 'Bot'):
    await bot.add_cog(BombParty(bot), settings_template=settings_template)
