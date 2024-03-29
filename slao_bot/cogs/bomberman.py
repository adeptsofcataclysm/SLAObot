from collections import defaultdict
from typing import Dict, Optional

import discord
import tenacity
from discord import Colour, Embed, app_commands
from discord.ext import commands
from utils.wcl_client import WCLClient


class Bomberman(commands.Cog):

    _engineers: Dict
    _bomb_damage: Dict[str, int]
    _other_damage: Dict[str, int]

    def __init__(self):
        """Cog to check potions used during a raid."""
        self._engineers = defaultdict()
        self._bomb_damage = defaultdict()
        self._other_damage = defaultdict()
        self.embed_title: str = 'Бомбим!'

    @app_commands.command(description='Использование гранат и схожих расходников')
    @app_commands.describe(report_id='WCL report ID')
    async def engineers(self, interaction: discord.Interaction, report_id: str) -> None:
        """Get data about bombs and bombs-like items used."""
        # noinspection PyUnresolvedReferences
        await interaction.response.defer()

        embed = await self.process_interaction(report_id)
        await interaction.edit_original_response(embed=embed)

    async def process_interaction(self, report_id: str) -> Optional[discord.Embed]:
        async with WCLClient() as client:
            try:
                rs = await client.get_bombs(report_id)
            except tenacity.RetryError:
                return None

        self.make_engineers(rs['reportData']['report']['engineers']['data']['entries'])
        self._bomb_damage = self.calculate_damage(rs['reportData']['report']['bombs']['data']['entries'])
        self._bomb_damage = dict(sorted(self._bomb_damage.items(), key=lambda item: item[1], reverse=True))
        self._other_damage = self.calculate_damage(rs['reportData']['report']['others']['data']['entries'])
        self._other_damage = dict(sorted(self._other_damage.items(), key=lambda item: item[1], reverse=True))

        embed = Embed(
            title=self.embed_title,
            description='Использование гранат и схожих расходников. Много гранат - быстрее пройден рейд.',
            colour=Colour.teal(),
        )
        embed.set_author(
            name='Элитный отряд синих гренадёров',
            url='',
            icon_url='https://cdn.icon-icons.com/icons2/1465/PNG/64/409bomb_100833.png',
        )

        embed.add_field(name='Сапёры', value=self.print_engineers(), inline=False)
        embed.add_field(name='Их соратники', value=self.print_others(), inline=False)

        self._engineers.clear()
        self._bomb_damage.clear()
        self._other_damage.clear()

        return embed

    def calculate_damage(self, entries: Dict) -> Dict:
        damage = {}
        if len(entries) == 0:
            return damage
        for entry in entries:
            if 'subentries' in entry:
                for subentry in entry['subentries']:
                    damage = self._add_damage(subentry, damage)
            else:
                damage = self._add_damage(entry, damage)

        return damage

    def make_engineers(self, entries: Dict) -> None:
        if len(entries) == 0:
            return
        for entry in entries:
            self._engineers[entry['id']] = entry['name']

        return

    def print_engineers(self) -> str:
        if len(self._bomb_damage) == 0:
            return 'Вагонимся'

        value = ''
        for raider_name, raider_damage in self._bomb_damage.items():
            if len(value) > 940:
                return value + 'И исчо немного народа.'
            if len(value) > 0:
                value += ', '

            value += f'{raider_name}({raider_damage})'
            self._engineers = {key: val for key, val in self._engineers.items() if val != raider_name}

        if len(self._engineers) > 0:
            for _raider_id, raider_name in self._engineers.items():
                if len(value) > 940:
                    return value + 'И исчо немного народа.'
                if len(value) > 0:
                    value += ', '

                value += f'{raider_name}(0)'

        return value

    def print_others(self) -> str:
        if len(self._other_damage) == 0:
            return 'Не завезли'

        value = ''
        for raider_name, raider_damage in self._other_damage.items():
            if len(value) > 940:
                return value + 'И исчо немного народа.'
            if len(value) > 0:
                value += ', '

            value += f'{raider_name}({raider_damage})'

        return value

    @staticmethod
    def _add_damage(raider: Dict, result: Dict) -> Dict:
        if raider['actorType'] == 'TricksOfTheTrade':
            return result
        if raider['actorName'] in result:
            result[raider['actorName']] += raider['total']
        else:
            result[raider['actorName']] = raider['total']

        return result


async def setup(bot):
    await bot.add_cog(Bomberman())
