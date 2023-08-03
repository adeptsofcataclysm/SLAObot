from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict

import tenacity
from discord import Colour, Embed
from discord.ext import commands
from discord.ext.commands import Context
from utils.constants import POT_IMAGES
from utils.report import Report
from utils.wcl_client import WCLClient


@dataclass
class RaidConsumables:
    hp_mana_pots: Dict[str, int] = field(default_factory=defaultdict)
    hp_mana_stones: Dict[str, int] = field(default_factory=defaultdict)
    combat_potions: Dict[str, int] = field(default_factory=defaultdict)
    combat_prepotions: Dict[str, int] = field(default_factory=defaultdict)
    combat_total: Dict[str, int] = field(default_factory=defaultdict)

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

    def process_prepotions(self, raiders, events) -> None:
        return

    def calculate_total(self) -> None:
        return


class Potions(commands.Cog):
    def __init__(self, bot):
        """Cog to check potions used during a raid.

        :param bot:
        """
        self.bot = bot

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

        raiders_by_role = Report.get_raiders_by_role(table_summary)

        consumables = RaidConsumables()
        consumables.clear_data()
        consumables.process_hp_mana_pots(rs['reportData']['report']['hp_mana_pots']['data']['entries'])
        consumables.process_hp_mana_stones(rs['reportData']['report']['hp_mana_stones']['data']['entries'])
        consumables.process_combat_potions(rs['reportData']['report']['combat_pots']['data']['entries'])

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
                        value=self._print_pot_usage(consumables.combat_potions),
                        inline=False)

        if ctx.message.author != self.bot.user:
            await ctx.send(embed=embed)
        else:
            embeds = ctx.message.embeds
            embeds.append(embed)
            await ctx.message.edit(embeds=embeds)

    @staticmethod
    def _print_pot_usage(entries: Dict) -> str:
        result = ''
        for key, value in entries.items():
            if len(result) > 980:
                return result
            if len(result) > 0:
                result += ', '
            result += f'{key}({value})'

        return result if len(result) > 0 else 'Вагонимся'


async def setup(bot):
    await bot.add_cog(Potions(bot))
