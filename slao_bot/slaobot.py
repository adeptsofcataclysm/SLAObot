from typing import Any

import discord
from discord import Message, RawReactionActionEvent, TextChannel
from discord.ext import commands
from utils.config import settings

extensions = (
    'cogs.raidreport',
    'cogs.potions',
    'cogs.signup',
    'cogs.gear',
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


def _validate_reaction_payload(payload: RawReactionActionEvent, bot: commands.Bot, emoji: str) -> bool:
    """Validates payload for reactions based cogs.

    Reaction should be from user.
    Emoji should be same as provided.

    :param payload: Reaction Event Payload.
    :param bot: Bot instance.
    :param emoji: Emoji to check.
    :return:  True if validation passed.
    """
    if payload.user_id == bot.user.id:
        return False
    if payload.emoji.name != emoji:
        return False
    return True


async def _validate_reaction_message(payload: RawReactionActionEvent, bot: commands.Bot) -> Any:
    """Validates message for reactions based cogs.

    Message should be from bot.
    Message should have embed.

    :param payload: Reaction event payload.
    :param bot: Bot instance.
    :return: Returns message and message channel or None if validation failed.
    """
    channel = bot.get_channel(payload.channel_id)
    if channel is None:
        return None

    message = await channel.fetch_message(payload.message_id)
    if message is None:
        return None
    if message.author != bot.user:
        return None
    if len(message.embeds) < 1:
        return None

    return channel, message

if __name__ == '__main__':
    SlaoBot().run(settings.discord_token)
