import discord
from discord import Message, TextChannel
from discord.ext import commands

from utils.config import settings

extensions = (
    'cogs.raidreport',
    'cogs.potions',
    'cogs.signup',

)


class SlaoBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents(
            guilds=True,
            members=True,
            emojis=True,
            messages=True,
            reactions=True,
        )

        super().__init__(
            command_prefix=f'{settings.command_prefix}',
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.listening, name=f'{settings.command_prefix}'),
        )

        for extension in extensions:
            self.load_extension(extension)

    async def on_ready(self) -> None:
        print(f'We have logged in as {self.user}')
        print(f'Command prefix is: {self.command_prefix}')

    async def on_message(self, message: Message) -> None:
        if message.guild is None:
            return
        if message.author == self.user:
            return
        await self.process_commands(message)

    async def on_message_edit(self, before: Message, after: Message) -> None:
        if before.content != after.content:
            await self.on_message(after)


async def _delete_reply(channel: TextChannel, message: Message) -> None:
    async for msg in channel.history(limit=200, after=message.created_at):
        if msg.reference and msg.reference.message_id == message.id:
            await msg.delete()


if __name__ == '__main__':
    SlaoBot().run(settings.discord_token)
