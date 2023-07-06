from typing import Dict

import tenacity
from discord import Colour, Embed
from discord.ext import commands
from discord.ext.commands import Context
from utils.constants import POT_IMAGES
from utils.wcl_client import WCLClient


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
            except tenacity.RetryError:
                return

        embed = Embed(title='Расходники', description='Пьём по КД, крутим логи!', colour=Colour.teal())
        embed.add_field(name=POT_IMAGES.get('mana'),
                        value=self._get_pot_usage_sorted(rs['reportData']['report']['mana']['data']['entries']),
                        inline=False)

        embed.add_field(name=POT_IMAGES.get('hp'),
                        value=self._get_pot_usage_sorted(rs['reportData']['report']['hp']['data']['entries']),
                        inline=False)

        embed.add_field(name=POT_IMAGES.get('hpmana'),
                        value=self._get_pot_usage_sorted(rs['reportData']['report']['hpmana']['data']['entries']),
                        inline=False)

        embed.add_field(name=POT_IMAGES.get('manarunes'),
                        value=self._get_pot_usage_sorted(rs['reportData']['report']['manarunes']['data']['entries']),
                        inline=False)

        embed.add_field(name=POT_IMAGES.get('combatpots'),
                        value=self._get_pot_usage_sorted(rs['reportData']['report']['combatpots']['data']['entries']),
                        inline=False)
        embeds = ctx.message.embeds
        embeds.append(embed)
        await ctx.message.edit(embeds=embeds)

    @staticmethod
    def _get_pot_usage_sorted(entries: Dict) -> str:
        pots = {}
        for entry in entries:
            pots[entry['name']] = entry['total']

        pots = sorted(pots.items(), key=lambda item: item[1], reverse=True)

        result = ''
        for key, value in pots:
            if len(result) > 0:
                result += ', '
            result += f'{key}({value})'

        return result if len(result) > 0 else 'Вагонимся'


async def setup(bot):
    await bot.add_cog(Potions(bot))
