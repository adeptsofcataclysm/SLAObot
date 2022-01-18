from typing import Any, Dict, List

import discord
import tenacity
from discord import Colour, Embed, RawReactionActionEvent
from discord.ext import commands
from discord.ext.commands import Context
from slaobot import _delete_reply
from utils import enchants
from utils.constants import Role
from utils.models import Raider
from utils.report import Report
from utils.sockets import MIN_GEM_ILEVEL, RARE_GEMS, SOCKETS
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
        raiders = self._make_raiders(rs)
        # Check gems and enchants
        empty_sockets, low_quality_gems, no_enchants, low_enchants = self.check_gear(raiders)

        embed.add_field(name='Нет камней',
                        value='Камни вставлены у всех!' if len(empty_sockets) == 0 else ', '.join(empty_sockets),
                        inline=False)
        embed.add_field(name='Стрёмные камни',
                        value='У всех нормальные камни!' if len(low_quality_gems) == 0 else ', '.join(low_quality_gems),
                        inline=False)
        embed.add_field(name='Не все энчанты',
                        value='Зачарованные!' if len(no_enchants) == 0 else ', '.join(no_enchants),
                        inline=False)
        embed.add_field(name='Стрёмные энчанты',
                        value='Empty',
                        inline=False)

        await ctx.reply(embed=embed)

    def check_gear(self, raiders: Dict[Role, List[Raider]]):
        empty_sockets = set()
        low_quality_gems = set()
        no_enchants = set()
        low_enchants = set()

        for role in raiders:
            for raider in raiders[role]:
                for item in raider.gear:
                    if not self._check_sockets(item):
                        empty_sockets.add(raider.name)
                    if not self._check_gems(item):
                        low_quality_gems.add(raider.name)
                    if not self._check_enchants(item):
                        no_enchants.add(raider.name)
                    if not self._check_enchants_quality(item):
                        low_enchants.add(raider.name)

        return empty_sockets, low_quality_gems, no_enchants, low_enchants

    @staticmethod
    def _make_raiders(rs: Dict[str, Any]) -> Dict[Role, List[Raider]]:
        """
        Makes dictionary with raiders and adds gear to each raider

        :param rs: Response from WCL API query
        :return: Dictionary with raiders
        """
        raiders_by_role = Report.get_raiders_by_role(rs)

        for role, report_section in ((Role.HEALER, 'healers'), (Role.TANK, 'tanks'), (Role.DPS, 'dps')):
            for char in rs['reportData']['report']['table']['data']['playerDetails'][report_section]:
                for raider in raiders_by_role[role]:
                    if raider.name == char['name']:
                        raider.gear = char['combatantInfo']['gear']
        return raiders_by_role

    @staticmethod
    def _check_sockets(item: Dict) -> bool:
        """
        Check that there are no empty sockets

        :param item: Dictionary with item info
        :return: True if check passed. False if check failed, e.g. socket(s) is empty
        """
        sockets_num = SOCKETS.get(item['id'])
        if sockets_num is None:
            # No sockets in item
            return True
        if 'gems' not in item:
            # No gems in sockets
            return True
        item_gems = item.get('gems')
        if len(item_gems) < sockets_num:
            # Gems not in all sockets
            return False
        # All checks passed
        return True

    @staticmethod
    def _check_gems(item: Dict) -> bool:
        """
        Check gems quality for socket gems

        :param item: Dictionary with item info
        :return: True if check passed. False if check failed, e.g. gem quality if lower then required
        """
        if 'gems' not in item:
            # Either no sockets or no gems. Empty socket already checked in another method
            return True

        return all(not (gem['itemLevel'] < MIN_GEM_ILEVEL and gem['id'] not in RARE_GEMS) for gem in item['gems'])

    @staticmethod
    def _check_enchants(item) -> bool:
        """
        Checks that item that should be enchanted is enchanted

        :param item: Dictionary with item info
        :return: True if check passed. False if check failed, e.g. missing enchant
        """
        if item['slot'] not in enchants.ENCHANTABLE_SLOT:
            # No need to check enchants for that slot
            return True
        if 'permanentEnchant' not in item:
            return False
        # All checks passed
        return True

    @staticmethod
    def _check_enchants_quality(item) -> bool:
        return True


def setup(bot):
    bot.add_cog(Gear(bot))