from typing import Dict

import discord
import tenacity
from discord import Colour, Embed, RawReactionActionEvent
from discord.ext import commands
from discord.ext.commands import Context
from slaobot import (
    _delete_reply, _validate_reaction_message, _validate_reaction_payload,
)
from utils.constants import POT_IMAGES
from utils.wcl_client import WCLClient


class Potions(commands.Cog):
    def __init__(self, bot):
        """Cog to check potions used during a raid.

        :param bot:
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        if payload.event_type != 'REACTION_ADD':
            return
        if not _validate_reaction_payload(payload, self.bot, '🧪'):
            return

        channel, message = await _validate_reaction_message(payload, self.bot)
        if message is None:
            return

        reaction = discord.utils.get(message.reactions, emoji='🧪')
        if reaction.count > 2:
            await reaction.remove(payload.member)
            return

        ctx = await self.bot.get_context(message)
        report_id = message.embeds[0].author.url.split('/')[-1]
        await self.process_pots(ctx, report_id)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent) -> None:
        if payload.event_type != 'REACTION_REMOVE':
            return
        if not _validate_reaction_payload(payload, self.bot, '🧪'):
            return

        channel, message = await _validate_reaction_message(payload, self.bot)
        if message is None:
            return

        await _delete_reply(channel, message)

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

        embed.add_field(name=POT_IMAGES.get('drums'),
                        value=self._get_pot_usage_sorted(rs['reportData']['report']['drums']['data']['entries']),
                        inline=False)

        embed.add_field(name=POT_IMAGES.get('herbs'),
                        value=self._get_pot_usage_sorted(rs['reportData']['report']['herbs']['data']['entries']),
                        inline=False)

        embed.add_field(name=POT_IMAGES.get('combatpots'),
                        value=self._get_pot_usage_sorted(rs['reportData']['report']['combatpots']['data']['entries']),
                        inline=False)

        await ctx.reply(embed=embed)

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


def setup(bot):
    bot.add_cog(Potions(bot))
