from typing import Dict, Any, List

import discord
import tenacity
from discord import Colour, Embed, RawReactionActionEvent
from discord.ext import commands
from discord.ext.commands import Context

from slaobot import _delete_reply
from utils.constants import Role
from utils.models import Raider
from utils.report import Report
from utils.sockets import SOCKETS
from utils.wcl_client import WCLClient


class Gear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        if payload.event_type != 'REACTION_ADD':
            return
        if payload.user_id == self.bot.user.id:
            return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message.author != self.bot.user:
            return
        if len(message.embeds) < 1:
            return

        if payload.emoji.name == '🛂':
            reaction = discord.utils.get(message.reactions, emoji='🛂')
            if reaction.count > 2:
                await reaction.remove(payload.member)
                return

            ctx = await self.bot.get_context(message)
            report_id = message.embeds[0].author.url.split('/')[-1]
            await self.process_gear(ctx, report_id)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent) -> None:
        if payload.event_type != 'REACTION_REMOVE':
            return
        if payload.user_id == self.bot.user.id:
            return
        if payload.emoji.name == '🛂':
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if message.author != self.bot.user:
                return
            await _delete_reply(channel, message)

    @commands.command(name='gear')
    async def gear_command(self, ctx: Context, report_id: str) -> None:
        """Get data about potions used. Format: <prefix>gear SOME_REPORT_ID."""
        await self.process_gear(ctx, report_id)

    async def process_gear(self, ctx: Context, report_id: str) -> None:
        async with WCLClient() as client:
            try:
                rs = await client.get_gear(report_id)
            except tenacity.RetryError:
                return

        embed = Embed(title='Камни и зачаровывание', description='Щас будет душно!', colour=Colour.teal())

        # Prepare gear list
        raiders = _make_raiders(rs)

        embed.add_field(name='Нет камней',
                        value=_make_empty_sockets(raiders),
                        inline=False)
        embed.add_field(name='Стрёмные камни',
                        value='Empty',
                        inline=False)
        embed.add_field(name='Не все энчанты',
                        value='Empty',
                        inline=False)
        embed.add_field(name='Стрёмные энчанты',
                        value='Empty',
                        inline=False)

        await ctx.reply(embed=embed)


def _make_raiders(rs: Dict[str, Any]) -> Dict[Role, List[Raider]]:
    raiders_by_role = Report.get_raiders_by_role(rs)

    for role, report_section in ((Role.HEALER, 'healers'), (Role.TANK, 'tanks'), (Role.DPS, 'dps')):
        for char in rs['reportData']['report']['table']['data']['playerDetails'][report_section]:
            for raider in raiders_by_role[role]:
                if raider.name == char['name']:
                    raider.gear = char['combatantInfo']['gear']
    return raiders_by_role


def _make_empty_sockets(raiders: Dict[Role, List[Raider]]) -> str:
    value = set()
    for raider in raiders[Role.DPS]:
        for item in raider.gear:
            sockets_num = SOCKETS.get(item['id'])
            if sockets_num is not None:
                item_gems = item.get('gems')
                if item_gems is None or len(item_gems) < sockets_num:
                    value.add(raider.name)

    return ', '.join(value)


def setup(bot):
    bot.add_cog(Gear(bot))
