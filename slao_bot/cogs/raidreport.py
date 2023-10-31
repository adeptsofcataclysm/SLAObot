# -*- coding: utf-8 -*-
from typing import Any, Dict, Optional

import discord
import tenacity
from discord import Colour, Embed, Message, app_commands
from discord.ext import commands
from slaobot import SlaoBot
from utils.constants import ZONE_IMAGES, Role
from utils.format import bold, make_execution
from utils.raidview import RaidView
from utils.report import Report
from utils.wcl_client import WCLClient


class RaidReport(commands.Cog):
    def __init__(self, bot: SlaoBot):
        """Cog to provide basic statistics about raid.

        :param bot: Bot instance
        """
        self.bot: SlaoBot = bot
        self.bot.add_view(RaidView())

    @app_commands.command(description='Отчёт по логу на WCL')
    @app_commands.describe(report_id='WCL report ID')
    async def report(self, interaction: discord.Interaction, report_id: str) -> None:
        """Get data from WCL report."""
        # noinspection PyUnresolvedReferences
        await interaction.response.defer()

        embed = await self.process_interaction(report_id)
        await interaction.edit_original_response(embed=embed, view=RaidView())

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        """Replace original message from WarcraftLogs with interstitial message and later on with full report."""
        if message.author.display_name != 'WCL':
            return
        if not message.embeds:
            return

        report_id = message.embeds[0].url.split('/')[-1]
        if not report_id:
            return
        author_icon = message.embeds[0].thumbnail.url

        # We have message from WCL with embed and report_id. Let's rock!
        # Delete original WCL message
        ctx = await self.bot.get_context(message)
        await ctx.message.delete()

        # Send interstitial embed to store report_id
        embed = self._make_waiting_embed(report_id, author_icon)
        waiting_message = await ctx.send(embed=embed)

        embed = await self.process_interaction(report_id, author_icon=author_icon)
        if embed is None:
            await waiting_message.edit(view=RaidView())

        await waiting_message.edit(embed=embed, view=RaidView())

    async def process_interaction(self, report_id: str, **kwargs: Any) -> Optional[discord.Embed]:
        """Process a single report

        :param report_id: WarcraftLogs report ID
        """
        async with WCLClient() as client:
            try:
                rs = await client.get_rankings(report_id)
                table_summary = await client.get_table_summary(report_id)
            except tenacity.RetryError:
                return None

        report_title = rs['reportData']['report'].get('title', Report.make_report_title(rs))

        if rs['reportData']['report']['guildTag']:
            report_tag = rs['reportData']['report']['guildTag']['name']
        else:
            report_tag = 'No tag'

        report_url = f'https://classic.warcraftlogs.com/reports/{report_id}'
        report_description = Report.make_report_description(rs)
        author_icon = kwargs.get('author_icon', self.bot.user.avatar.url)

        embed = Embed(title=f'{report_title} - {report_tag}',
                      url=report_url,
                      description=report_description,
                      color=0xb51cd4)

        report_owner = rs['reportData']['report']['owner']['name']
        embed.set_author(name=report_owner, url=report_url, icon_url=author_icon)
        embed.set_image(url=ZONE_IMAGES.get(Report.get_report_zone_id(rs), ZONE_IMAGES.get(0)))

        if rs['reportData']['report']['zone']['frozen']:
            return

        # Add bosses, speed and execution
        self._make_fights(rs, embed)
        # Add raiders
        self._make_raiders(embed, table_summary)
        # Add links
        self._make_links(embed, report_id)

        return embed

    @staticmethod
    def _make_fights(rs: Dict[str, Any], embed: Embed) -> None:
        fights = rs['reportData']['report']['rankings']['data']

        if len(fights) == 0:
            embed.add_field(name='Лог пустой', value='Пора побеждать боссов!', inline=False)
            return

        if fights[-1]['fightID'] == 10000 or fights[-1]['fightID'] == 10001:
            embed.add_field(name='⚔️Полная зачистка', value=Report.make_fight_info(fights[-1]), inline=False)
        elif len(fights) <= 4:
            for fight in fights:
                embed.add_field(
                    name='⚔️' + fight['encounter']['name'],
                    value=Report.make_fight_info(fight),
                    inline=False,
                )
        else:
            bosses = ''
            execution = 0
            speed = 0
            for fight in fights:
                bosses += f"⚔{bold(fight['encounter']['name'])} "
                execution += fight['execution']['rankPercent']
                speed += fight['speed']['rankPercent']

            value = f'Исполнение: {bold(make_execution(int(execution / len(fights))))}\n'
            value += f'Скорость: {bold(int(speed / len(fights)))}%'

            if len(bosses) > 255:
                bosses = '⚔️Мноха Боссаф'

            embed.add_field(name=bosses, value=value, inline=False)

    @staticmethod
    def _make_raiders(embed: discord.Embed, rs: Dict[str, Any]) -> None:
        raiders_by_role = Report.get_raiders_by_role(rs)

        embed.add_field(name='Танки', value=Report.make_spec(raiders_by_role[Role.TANK]), inline=False)
        embed.add_field(
            name='Дамагеры',
            value=Report.make_spec(raiders_by_role[Role.DPS], show_trophy=True),
            inline=False,
        )
        embed.add_field(
            name='Лекари',
            value=Report.make_spec(raiders_by_role[Role.HEALER], show_trophy=True),
            inline=False,
        )

    @staticmethod
    def _make_links(embed: discord.Embed, report_id: str) -> None:
        wipefest = '<:wipefest_gg:1127888435697430548> [Wipefest]'
        wipefest += f'(https://www.wipefest.gg/report/{report_id}?gameVersion=warcraft-classic)'
        wowanalyzer = '<:wowanalyzer:1127894170565083156> [WoWAnalyzer]'
        wowanalyzer += f'(https://www.wowanalyzer.com/report/{report_id})'
        embed.add_field(name='На подумать', value=f'{wipefest} | {wowanalyzer}')

    @staticmethod
    def _make_waiting_embed(report_id: str, author_icon: str) -> discord.Embed:
        report_url = f'https://classic.warcraftlogs.com/reports/{report_id}'
        embed = Embed(
            title='Новый лог подъехал',
            description='Получаю данные с WarcraftLogs',
            colour=Colour.orange(),
            url=report_url)
        embed.set_thumbnail(url=author_icon)
        embed.set_footer(text='Иногда WCL тормозит, пичалька.')

        return embed


async def setup(bot):
    await bot.add_cog(RaidReport(bot))
