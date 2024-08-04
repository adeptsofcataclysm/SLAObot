import logging

import discord
from discord import Message
from discord.ext import commands
from discord.ext.commands import ExtensionFailed, Context
from utils.config import base_config, guild_config, default_config

extensions = (
    'cogs.raidreport',
    'cogs.potions',
    'cogs.signup',
    'cogs.gear',
    'cogs.bomberman',
    'cogs.damage',
    'cogs.epgp',
)


class SlaoBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents(
            guilds=True,
            members=True,
            messages=True,
            message_content=True,
            emojis=True,
        )
        logging.basicConfig(level=base_config['BASE']['LOG_LEVEL'])

        super().__init__(
            command_prefix=f"{base_config['BASE']['COMMAND_PREFIX']}",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.listening,
                                      name=f"{base_config['BASE']['COMMAND_PREFIX']}"),
        )

    async def setup_hook(self) -> None:
        for extension in extensions:
            try:
                await self.load_extension(extension)
            except ExtensionFailed:
                logging.exception(f'Failed to load extension {extension}.')

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

    async def on_guild_join(self, guild):
        guild_id = f'{guild.id}'
        if guild_config.has_section(guild_id):
            return

        guild_config.add_section(guild_id)
        guild_config[guild_id] = default_config
        guild_config[guild_id]['GUILD_NAME'] = guild.name
        with open('./config/guild.cfg', 'w') as configfile:
            guild_config.write(configfile)

        return

    @commands.command(name='sync')
    async def sync_command(self, ctx: Context) -> None:
        """Sync slash commands for a particular guild."""
        await self.tree.sync(guild=ctx.guild)


if __name__ == '__main__':
    SlaoBot().run(base_config['BASE']['DISCORD_TOKEN'])
