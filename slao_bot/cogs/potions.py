from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List

import tenacity
from discord import Colour, Embed
from discord.ext import commands
from discord.ext.commands import Context
from utils.constants import POT_IMAGES
from utils.wcl_client import WCLClient


@dataclass
class RaidConsumables:
    hp_mana_pots: Dict[str, int] = field(default_factory=defaultdict)
    hp_mana_stones: Dict[str, int] = field(default_factory=defaultdict)
    combat_potions: Dict[str, int] = field(default_factory=defaultdict)
    combat_prepotions: Dict[str, int] = field(default_factory=defaultdict)
    combat_total: Dict[str, List] = field(default_factory=defaultdict)

    def clear_data(self) -> 'RaidConsumables':
        self.hp_mana_pots = defaultdict()
        self.hp_mana_stones = defaultdict()
        self.combat_potions = defaultdict()
        self.combat_prepotions = defaultdict()
        self.combat_total = defaultdict()

        return self

    def process_hp_mana_pots(self, entries: Dict) -> None:
        for entry in entries:
            self.hp_mana_pots[entry['name']] = entry['total']

        self.hp_mana_pots = dict(sorted(self.hp_mana_pots.items(), key=lambda item: item[1], reverse=True))

    def process_hp_mana_stones(self, entries: Dict) -> None:
        for entry in entries:
            self.hp_mana_stones[entry['name']] = entry['total']

        self.hp_mana_stones = dict(sorted(self.hp_mana_stones.items(), key=lambda item: item[1], reverse=True))

    def process_combat_potions(self, entries: Dict) -> None:
        for entry in entries:
            self.combat_potions[entry['name']] = entry['total']

        self.combat_potions = dict(sorted(self.combat_potions.items(), key=lambda item: item[1], reverse=True))

    def process_prepotions(self, raiders: Dict[int, str], entries: Dict) -> None:
        for entry in entries:
            if entry['type'] != 'combatantinfo':
                continue
            for aura in entry['auras']:
                if aura['ability'] == 53762 or aura['ability'] == 53908 or aura['ability'] == 53909:
                    self.combat_prepotions[raiders[entry['sourceID']]] = self.combat_prepotions.get(
                        raiders[entry['sourceID']], 0) + 1

        self.combat_prepotions = dict(sorted(self.combat_prepotions.items(), key=lambda item: item[1], reverse=True))

    def calculate_total(self) -> None:

        for key in self.combat_potions:
            self.combat_total[key] = [
                self.combat_potions[key],
                self.combat_prepotions.get(key, 0),
                self.combat_potions[key] + self.combat_prepotions.get(key, 0),
            ]

        for key in self.combat_prepotions:
            if key not in self.combat_total:
                self.combat_total[key] = [0, self.combat_prepotions[key], self.combat_prepotions[key]]

        self.combat_total = dict(sorted(self.combat_total.items(), key=lambda item: item[1][2], reverse=True))


class Potions(commands.Cog):
    def __init__(self, bot):
        """Cog to check potions used during a raid.

        :param bot:
        """
        self.bot = bot

    @staticmethod
    def raiders_by_id(rs: Dict[str, Any]) -> Dict[int, str]:
        raiders = rs['reportData']['report']['table']['data']['composition']
        result = defaultdict()

        for raider in raiders:
            result[raider['id']] = raider['name']

        return result

    @commands.command(name='pot')
    async def pot_command(self, ctx: Context, report_id: str) -> None:
        """Get data about potions used. Format: <prefix>pot SOME_REPORT_ID."""
        await self.process_pots(ctx, report_id)

    async def process_pots(self, ctx: Context, report_id: str) -> None:
        async with WCLClient() as client:
            try:
                rs = await client.get_pots(report_id)
                table_summary = await client.get_table_summary(report_id)
                events_info = await client.get_events_combatantinfo(report_id)
            except tenacity.RetryError:
                return

        raiders_by_id = self.raiders_by_id(table_summary)

        consumables = RaidConsumables()
        consumables.clear_data()
        consumables.process_hp_mana_pots(rs['reportData']['report']['hp_mana_pots']['data']['entries'])
        consumables.process_hp_mana_stones(rs['reportData']['report']['hp_mana_stones']['data']['entries'])
        consumables.process_combat_potions(rs['reportData']['report']['combat_pots']['data']['entries'])
        consumables.process_prepotions(raiders_by_id, events_info['reportData']['report']['events']['data'])
        consumables.calculate_total()

        embed = Embed(title='Потная катка', description='Пьём по КД, крутим логи.', colour=Colour.teal())
        embed.set_author(
            name='Синяя яма',
            url='',
            icon_url='https://cdn.icon-icons.com/icons2/2419/PNG/64/beer_drink_icon_146844.png',
        )
        embed.add_field(name=POT_IMAGES.get('hp_mana_pots') + 'Зелья маны и здоровья',
                        value=self._print_pot_usage(consumables.hp_mana_pots),
                        inline=False)

        embed.add_field(name=POT_IMAGES.get('hp_mana_stones') + 'Камни маны и здоровья',
                        value=self._print_pot_usage(consumables.hp_mana_stones),
                        inline=False)

        embed.add_field(name=POT_IMAGES.get('combat_pots') + 'Боевые зелья',
                        value=self._print_pot_total(consumables.combat_total),
                        inline=False)

        if ctx.message.author != self.bot.user:
            await ctx.send(embed=embed)
        else:
            embeds = ctx.message.embeds
            embeds.append(embed)
            await ctx.message.edit(embeds=embeds)

    @staticmethod
    def _print_pot_usage(entries: Dict[str, int]) -> str:
        result = ''
        for key, value in entries.items():
            if len(result) > 950:
                return result + 'И исчо немного народа.'
            if len(result) > 0:
                result += ', '
            result += f'{key}({value})'

        return result if len(result) > 0 else 'Вагонимся'

    @staticmethod
    def _print_pot_total(entries: Dict[str, List]) -> str:
        result = ''
        for key, value in entries.items():
            if len(result) > 950:
                return result + 'И исчо немного народа.'
            if len(result) > 0:
                result += ', '
            result += f'{key}({value[1]} + {value[0]})'

        return result if len(result) > 0 else 'Вагонимся'


async def setup(bot):
    await bot.add_cog(Potions(bot))
