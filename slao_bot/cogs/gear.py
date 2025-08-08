import sqlite3
from collections import defaultdict
from dataclasses import dataclass, field
from itertools import chain
from sqlite3 import Connection, Cursor
from typing import Any, Dict, Iterable, List, Optional, Set

import discord
import tenacity
from discord import Colour, Embed, app_commands
from discord.ext import commands
from utils import enchants
from utils.config import guild_config
from utils.constants import SLOT_NAMES, Role
from utils.models import Raider
from utils.report import Report
from utils.sockets import MIN_GEM_ILEVEL, SOCKETS
from utils.wcl_client import WCLClient

from slaobot import SlaoBot


@dataclass
class RaidWeakEquipment:
    empty_sockets: Dict[str, Set] = field(default_factory=defaultdict)
    low_quality_gems: Dict[str, Set] = field(default_factory=defaultdict)
    no_enchants: Dict[str, Set] = field(default_factory=defaultdict)
    low_enchants: Dict[str, Set] = field(default_factory=defaultdict)
    offspec_raid: Dict[str, Set] = field(default_factory=defaultdict)

    def from_raiders(self, raiders: Iterable[Raider], guild_id: str, raid_time: int) -> 'RaidWeakEquipment':
        self.empty_sockets = defaultdict(set)
        self.low_quality_gems = defaultdict(set)
        self.no_enchants = defaultdict(set)
        self.low_enchants = defaultdict(set)
        self.offspec_raid = defaultdict(set)

        for raider in raiders:
            for item in raider.gear:
                if item['id'] == 0:
                    continue
                self._check_sockets(raider.name, item)
                self._check_enchants(raider.name, item)
                if guild_config.has_section(guild_id) and guild_config[guild_id].getboolean('epgp_enabled'):
                    self._check_offspec(raider.name, item, guild_id, raid_time)

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
            # All sockets are gemmed. Let's check gems level
        else:
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
        elif item['permanentEnchant'] not in enchants.GOOD_ENCHANTS[item['slot']]:
            self.low_enchants[raider_name].add(SLOT_NAMES.get(item['slot']))

    def _check_offspec(self, raider_name: str, item: Dict, guild_id: str, raid_time: int) -> None:
        """Checks if items looted for off-spec during month before raid were equipped in raid

        :param raider_name: Raider name
        :param item:  Equipped item dictionary
        :param guild_id: Discord Guild ID. Used to query a proper DB
        :param raid_time: Start time of the raid
        """
        db_name = f'./data/{guild_id}.db'
        connection: Connection = sqlite3.connect(db_name)
        cursor: Cursor = connection.cursor()

        cursor.execute('''SELECT * FROM Traffic WHERE
        item_id=? AND target=? AND (gpa - gpb)=0 AND timestamp BETWEEN ? and ? ''',
                       (item['id'], raider_name, raid_time - 2592000, raid_time),
                       )
        if not cursor.fetchone() is None:
            self.offspec_raid[raider_name].add(SLOT_NAMES.get(item['slot']))

        cursor.close()
        connection.close()


class Gear(commands.Cog):

    def __init__(self):
        """Cog to check gems and enchants."""
        self.embed_title: str = 'Камни и зачаровывание'

    @app_commands.command(description='Камни и энчанты')
    @app_commands.describe(report_id='WCL report ID')
    async def gear(self, interaction: discord.Interaction, report_id: str) -> None:
        """Get data about missing or low-level gems and enchants."""
        # noinspection PyUnresolvedReferences
        await interaction.response.defer()

        embed = await self.process_interaction(report_id, str(interaction.guild.id))
        await interaction.edit_original_response(embed=embed)

    async def process_interaction(self, report_id: str, guild_id: str) -> Optional[discord.Embed]:
        async with WCLClient() as client:
            try:
                rs = await client.get_table_summary(report_id)
            except tenacity.RetryError:
                return

        embed = Embed(title=self.embed_title, description='Щас будет душно!', colour=Colour.teal())
        embed.set_author(
            name='Лавка зачарованных самоцветов',
            url='',
            icon_url='https://cdn.icon-icons.com/icons2/3580/PNG/64/'
                     'value_jewellery_gem_finance_diamond_icon_225769.png',
        )

        # Prepare gear list
        raiders = self._make_raiders(rs)
        # Check gems and enchants
        equipment = RaidWeakEquipment()
        raid_time = int(rs['reportData']['report']['startTime'] / 1000)
        equipment.from_raiders(chain.from_iterable(raiders.values()), guild_id, raid_time)

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
        if guild_config.has_section(guild_id) and guild_config[guild_id].getboolean('epgp_enabled'):
            embed.add_field(
                name='Оффспек лут в рейде',
                value=self._print_raiders(equipment.offspec_raid) or 'Все молодцы!',
                inline=False,
            )

        return embed

    @staticmethod
    def _print_raiders(gear_issues: Dict[str, Set]) -> Optional[str]:
        if len(gear_issues) == 0:
            return None
        value = ''

        for index, raider in enumerate(gear_issues):
            if len(value) > 940:
                return value + 'И исчо немного вагонов.'
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


async def setup(bot: SlaoBot) -> None:
    await bot.add_cog(Gear())
