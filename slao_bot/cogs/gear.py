from collections import defaultdict
from dataclasses import dataclass, field
from itertools import chain
from typing import Any, Dict, Iterable, List, Optional, Set

import discord
import tenacity
from discord import Colour, Embed, RawReactionActionEvent
from discord.ext import commands
from discord.ext.commands import Context
from slaobot import (
    _delete_reply, _validate_reaction_message, _validate_reaction_payload,
)
from utils import enchants
from utils.constants import SLOT_NAMES, Role
from utils.models import Raider
from utils.report import Report
from utils.sockets import MIN_GEM_ILEVEL, SOCKETS
from utils.wcl_client import WCLClient


@dataclass
class RaidWeakEquipment:
    empty_sockets: Dict[str, Set] = field(default_factory=defaultdict)
    low_quality_gems: Dict[str, Set] = field(default_factory=defaultdict)
    no_enchants: Dict[str, Set] = field(default_factory=defaultdict)
    low_enchants: Dict[str, Set] = field(default_factory=defaultdict)

    def from_raiders(self, raiders: Iterable[Raider]) -> 'RaidWeakEquipment':
        self.empty_sockets = defaultdict(set)
        self.low_quality_gems = defaultdict(set)
        self.no_enchants = defaultdict(set)
        self.low_enchants = defaultdict(set)

        for raider in raiders:
            for item in raider.gear:
                if item['id'] == 0:
                    continue
                self._check_sockets(raider.name, item)
                self._check_enchants(raider.name, item)

        return self

    def _check_sockets(self, raider_name: str, item: Dict) -> None:
        """Check item for missing or low quality gems

        :param raider_name: Raider name
        :param item: Equipped item dictionary
        """
        sockets_num = SOCKETS.get(item['id'])
        if sockets_num is None:
            # No sockets in item
            return
        if 'gems' not in item or len(item.get('gems')) < sockets_num:
            # No gems in sockets
            self.empty_sockets[raider_name].add(SLOT_NAMES.get(item['slot']))
        else:
            # All sockets are gemmed. Let's check gems level
            for gem in item['gems']:
                if gem['itemLevel'] < MIN_GEM_ILEVEL:
                    self.low_quality_gems[raider_name].add(SLOT_NAMES.get(item['slot']))

    def _check_enchants(self, raider_name: str, item: Dict) -> None:
        """Checks item for missing or low quality enchant

        :param raider_name: Raider name
        :param item: Equipped item dictionary
        """
        if item['slot'] not in enchants.ENCHANTABLE_SLOT:
            # No need to check enchants for that slot
            return
        if item['id'] in enchants.EXCLUDED_GEAR:
            return
        if 'permanentEnchant' not in item:
            self.no_enchants[raider_name].add(SLOT_NAMES.get(item['slot']))
        elif item['permanentEnchant'] in enchants.BAD_ENCHANTS[item['slot']]:
            self.low_enchants[raider_name].add(SLOT_NAMES.get(item['slot']))


class Gear(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """Cog to check gems and enchants.

        :param bot: Bot instance
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        if payload.event_type != 'REACTION_ADD':
            return
        if not _validate_reaction_payload(payload, self.bot, '🛂'):
            return

        _, message = await _validate_reaction_message(payload, self.bot)
        if message is None:
            return

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
        if not _validate_reaction_payload(payload, self.bot, '🛂'):
            return

        channel, message = await _validate_reaction_message(payload, self.bot)
        if message is None:
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
        equipment = RaidWeakEquipment()
        equipment.from_raiders(chain.from_iterable(raiders.values()))

        embed.add_field(
            name='Нет камней',
            value=self._print_raiders(equipment.empty_sockets) or 'Камни вставлены у всех!',
            inline=False,
        )
        embed.add_field(
            name='Стрёмные камни',
            value=self._print_raiders(equipment.low_quality_gems) or 'У всех нормальные камни!',
            inline=False,
        )
        embed.add_field(
            name='Не все энчанты',
            value=self._print_raiders(equipment.no_enchants) or 'Зачарованные!',
            inline=False,
        )
        embed.add_field(
            name='Стрёмные энчанты',
            value=self._print_raiders(equipment.low_enchants) or 'С пивком потянет!',
            inline=False,
        )

        await ctx.reply(embed=embed)

    @staticmethod
    def _print_raiders(gear_issues: Dict[str, Set]) -> Optional[str]:
        if len(gear_issues) == 0:
            return None
        value = ''

        for index, raider in enumerate(gear_issues):
            if len(value) > 980:
                return value
            if index > 0:
                value += ', '
            value += raider
            value += '('
            value += ', '.join(gear_issues[raider])
            value += ')'

        return value

    @staticmethod
    def _make_raiders(rs: Dict[str, Any]) -> Dict[Role, List[Raider]]:
        """Makes dictionary with raiders and adds gear to each raider

        :param rs: Response from WCL API query
        :return: Dictionary with raiders
        """
        raiders_by_role = Report.get_raiders_by_role(rs)

        for role, report_section in ((Role.HEALER, 'healers'), (Role.TANK, 'tanks'), (Role.DPS, 'dps')):
            for char in rs['reportData']['report']['table']['data']['playerDetails'][report_section]:
                for raider in raiders_by_role[role]:
                    if raider.name == char['name'] and char['combatantInfo']:
                        raider.gear = char['combatantInfo']['gear']
                        continue
        return raiders_by_role


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Gear(bot))
