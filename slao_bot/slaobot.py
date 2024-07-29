import logging

import discord
from discord import Message
from discord.ext import commands
from discord.ext.commands import ExtensionFailed
from utils.config import settings

extensions = (
    'cogs.raidreport',
    'cogs.potions',
    'cogs.signup',
    'cogs.gear',
    'cogs.bomberman',
    'cogs.damage',
    'cogs.epgp',
)

TEST_GUILD = discord.Object(873894278110265404)


class SlaoBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents(
            guilds=True,
            members=True,
            messages=True,
            message_content=True,
            emojis=True,
        )
        logging.basicConfig(level=logging.WARN)

        super().__init__(
            command_prefix=f'{settings.command_prefix}',
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.listening, name=f'{settings.command_prefix}'),
        )

    async def setup_hook(self) -> None:
        for extension in extensions:
            try:
                await self.load_extension(extension)
            except ExtensionFailed:
                logging.exception(f'Failed to load extension {extension}.')

        synced = await self.tree.sync()
        logging.info(synced)

    async def on_ready(self) -> None:
        logging.info(f'We have logged in as {self.user}')
        logging.info(f'Command prefix is: {self.command_prefix}')

    async def on_message(self, message: Message) -> None:
        if message.guild is None:
            return
        if message.author == self.user:
            return
        await self.process_commands(message)

    async def on_message_edit(self, before: Message, after: Message) -> None:
        if before.content != after.content:
            await self.on_message(after)


if __name__ == '__main__':
    SlaoBot().run(settings.discord_token)
