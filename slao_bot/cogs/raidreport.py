# -*- coding: utf-8 -*-
from typing import Any, Dict

import discord
import tenacity
from discord import Colour, Embed, Message, RawReactionActionEvent
from discord.ext import commands
from discord.ext.commands import Context
from slaobot import (
    _delete_reply, _validate_reaction_message, _validate_reaction_payload,
)
from utils.constants import ZONE_IMAGES, Role
from utils.format import bold, make_execution
from utils.report import Report
from utils.wcl_client import WCLClient


class RaidReport(commands.Cog):
    def __init__(self, bot):
        """Cog to provide basic statistics about raid.

        :param bot: Bot instance
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.display_name != 'WCL':
            return
        if not message.embeds:
            return

        report_id = message.embeds[0].url.split('/')[-1]
        author_icon = message.embeds[0].thumbnail.url
        if report_id:
            ctx = await self.bot.get_context(message)
            # Delete original WCL message
            await ctx.message.delete()
            await self.process_report(ctx, report_id, author_icon)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        if payload.event_type != 'REACTION_ADD':
            return
        if not _validate_reaction_payload(payload, self.bot, '🔄'):
            return

        channel, message = await _validate_reaction_message(payload, self.bot)
        if message is None:
            return

        if message.embeds[0].url:
            # Waiting embed
            report_id = message.embeds[0].url.split('/')[-1]
            author_icon = message.embeds[0].thumbnail.url
        else:
            # Rankings embed
            report_id = message.embeds[0].author.url.split('/')[-1]
            author_icon = message.embeds[0].author.icon_url

        # delete reply
        await _delete_reply(channel, message)
        # delete report
        await message.delete()

        ctx = await self.bot.get_context(message)
        await self.process_report(ctx, report_id, author_icon)

    @commands.command(name='wcl', aliases=['🍦'])
    async def wcl_command(self, ctx: Context, report_id: str) -> None:
        """Get data from report. Format: <prefix>wcl SOME_REPORT_ID."""
        author_icon = 'https://cdn.discordapp.com/icons/620682853709250560/6c53810d8a4e2b75069208a472465694.png'
        await self.process_report(ctx, report_id, author_icon)

    async def process_report(self, ctx: Context, report_id: str, author_icon: str) -> None:
        """Process a single report and sends embed to context channel

        :param ctx: Invocation context. Should be a channel
        :param report_id: WarcraftLogs report ID
        :param author_icon:
        """
        report_url = f'https://classic.warcraftlogs.com/reports/{report_id}'
        wait_embed = Embed(
            title='Новый лог подъехал',
            description='Получаю данные с WarcraftLogs',
            colour=Colour.orange(),
            url=report_url)
        wait_embed.set_thumbnail(url=author_icon)
        wait_embed.set_footer(text='Иногда WCL тормозит, пичалька.')
        waiting_embed = await ctx.send(embed=wait_embed)

        async with WCLClient() as client:
            try:
                rs = await client.get_data(report_id)
            except tenacity.RetryError:
                await waiting_embed.add_reaction('🔄')
                return

        report_title = Report.make_report_title(rs)
        report_description = Report.make_report_description(rs)
        embed = Embed(title=report_title, description=report_description, color=0xb51cd4)

        report_owner = rs['reportData']['report']['owner']['name']
        embed.set_author(name=report_owner, url=report_url, icon_url=author_icon)
        embed.set_image(url=ZONE_IMAGES.get(Report.get_report_zone_id(rs), ZONE_IMAGES.get(0)))

        # Print bosses, speed and execution
        if not rs['reportData']['report']['zone']['frozen']:
            await self._make_fights(rs, embed, waiting_embed)

        # Print raiders
        self._make_raiders(embed, rs)

        await waiting_embed.edit(embed=embed)

    @staticmethod
    async def _make_fights(rs: Dict[str, Any], embed: Embed, waiting_embed: Message) -> None:
        fights = rs['reportData']['report']['rankings']['data']

        if len(fights) == 0:
            embed.add_field(name='Лог пустой', value='Пора побеждать боссов!', inline=False)
            await waiting_embed.add_reaction('🔄')
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
            await waiting_embed.add_reaction('🔄')
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
            await waiting_embed.add_reaction('🔄')

        await waiting_embed.add_reaction('🧪')
        await waiting_embed.add_reaction('🛂')
        await waiting_embed.add_reaction('💣')

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


def setup(bot):
    bot.add_cog(RaidReport(bot))
