from collections import defaultdict
from typing import Dict, List

import tenacity
from discord import Colour, Embed
from discord.ext import commands
from discord.ext.commands import Context
from utils.constants import CLASS_COEFF, Role
from utils.models import Raider
from utils.report import Report
from utils.wcl_client import WCLClient


class Damage(commands.Cog):
    def __init__(self, bot):
        """Cog to check DPS of a raid members.

        :param bot:
        """
        self.bot = bot
        self.dps_threshold = 8500
        self.combat_time = 0

    @commands.command(name='damage')
    async def damage_command(self, ctx: Context, report_id: str) -> None:
        """Get data about damage done in raid. Format: <prefix>damage SOME_REPORT_ID."""
        await self.process_damage(ctx, report_id)

    async def process_damage(self, ctx: Context, report_id: str) -> None:
        async with WCLClient() as client:
            try:
                rs = await client.get_table_summary(report_id)
            except tenacity.RetryError:
                return

        filtered_raiders = self._adjust_damage(Report.get_raiders_by_role(rs)[Role.DPS])

        embed = Embed(
            title='DPS check!',
            description='Жми кнопки! Исчо сильнее и правильнее жми кнопки!',
            colour=Colour.teal(),
        )
        embed.set_author(
            name='Сын маминой подруги на ДК',
            url='',
            icon_url='https://cdn.icon-icons.com/icons2/1859/PNG/64/man16_117872.png',
        )

        raw_combat_time = rs['reportData']['report']['table']['data'].get('totalTime', 0)
        adjustment = rs['reportData']['report']['table']['data'].get('damageDowntime', 0)
        self.combat_time = raw_combat_time - adjustment

        if self.combat_time == 0:
            embed.add_field(name='Что-то пошло не так', value='Время в бою - 0', inline=False)
        else:
            embed.add_field(name='Памперы',
                            value=self.print_pumpers(filtered_raiders),
                            inline=False)

            embed.add_field(name='Вагоны',
                            value=self.print_low_dps(filtered_raiders),
                            inline=False)

        if ctx.message.author != self.bot.user:
            await ctx.send(embed=embed)
        else:
            embeds = ctx.message.embeds
            embeds.append(embed)
            await ctx.message.edit(embeds=embeds)

    def print_pumpers(self, raiders: Dict[int, Raider]) -> str:
        result = ''
        for _int, raider in raiders.items():
            if len(result) > 940:
                return result + 'И исчо немного народа.'
            if (raider.total / self.combat_time * 1000) >= self.dps_threshold:
                if len(result) > 0:
                    result += ', '
                result += raider.name

        return result if len(result) > 0 else 'Вагонимся'

    def print_low_dps(self, raiders: Dict[int, Raider]) -> str:
        result = ''
        for _int, raider in raiders.items():
            if len(result) > 940:
                return result + 'И исчо немного народа.'
            if (raider.total / self.combat_time * 1000) < self.dps_threshold:
                if len(result) > 0:
                    result += ', '
                result += raider.name

        return result if len(result) > 0 else 'Все молодцы'

    @staticmethod
    def _adjust_damage(all_specs_raiders: List[Raider]) -> Dict[int, Raider]:
        filtered_raiders = defaultdict(Raider)
        for raider in all_specs_raiders:
            if raider.raider_id in filtered_raiders:

                if (CLASS_COEFF[raider.class_][raider.spec]
                        < CLASS_COEFF[filtered_raiders[raider.raider_id].class_]
                        [filtered_raiders[raider.raider_id].spec]):
                    filtered_raiders[raider.raider_id].spec = raider.spec
            else:
                filtered_raiders[raider.raider_id] = raider

        for raider_id, raider in filtered_raiders.items():
            filtered_raiders[raider_id].total = (
                filtered_raiders[raider_id].total
                * CLASS_COEFF[raider.class_][raider.spec]
            )

        return filtered_raiders


async def setup(bot):
    await bot.add_cog(Damage(bot))
