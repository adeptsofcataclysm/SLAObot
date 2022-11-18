from typing import Dict

import discord
import tenacity
from discord import Colour, Embed, RawReactionActionEvent
from discord.ext import commands
from discord.ext.commands import Context
from slaobot import (
    _delete_reply, _validate_reaction_message, _validate_reaction_payload,
)
from utils.wcl_client import WCLClient


class Bomberman(commands.Cog):
    def __init__(self, bot):
        """Cog to check potions used during a raid.

        :param bot:
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        if payload.event_type != 'REACTION_ADD':
            return
        if not _validate_reaction_payload(payload, self.bot, '💣'):
            return

        channel, message = await _validate_reaction_message(payload, self.bot)
        if message is None:
            return

        reaction = discord.utils.get(message.reactions, emoji='💣')
        if reaction.count > 2:
            await reaction.remove(payload.member)
            return

        ctx = await self.bot.get_context(message)
        report_id = message.embeds[0].author.url.split('/')[-1]
        await self.process_bombs(ctx, report_id)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent) -> None:
        if payload.event_type != 'REACTION_REMOVE':
            return
        if not _validate_reaction_payload(payload, self.bot, '💣'):
            return

        channel, message = await _validate_reaction_message(payload, self.bot)
        if message is None:
            return

        await _delete_reply(channel, message)

    @commands.command(name='bomb')
    async def bomb_command(self, ctx: Context, report_id: str) -> None:
        """Get data about bombs and bombs-like items used. Format: <prefix>bomb SOME_REPORT_ID."""
        await self.process_bombs(ctx, report_id)

    async def process_bombs(self, ctx: Context, report_id: str) -> None:
        async with WCLClient() as client:
            try:
                rs = await client.get_bombs(report_id)
            except tenacity.RetryError:
                return

        engs = self._make_engineers(rs['reportData']['report']['engineers']['data']['entries'])
        dmg = self.calculate_damage(rs['reportData']['report']['bombs']['data']['entries'])
        other = self.calculate_damage(rs['reportData']['report']['others']['data']['entries'])

        embed = Embed(title='Бомбим!', description='Использование гранат и схожих расходников. '
                                                   'Много гранат - быстрее пройден рейд.', colour=Colour.teal())
        embed.set_author(name='Элитный отряд синих гренадёров', url='',
                         icon_url='https://cdn.icon-icons.com/icons2/1465/PNG/64/409bomb_100833.png')

        embed.add_field(name='Сапёры', value=self._print_engineers(engs, dmg), inline=False)
        embed.add_field(name='Их соратники', value=self._print_others(other), inline=False)

        await ctx.reply(embed=embed)

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

    @staticmethod
    def _make_engineers(entries: Dict) -> Dict:
        engineers = {}
        if len(entries) == 0:
            return engineers
        for entry in entries:
            engineers[entry['id']] = entry['name']

        return engineers

    @staticmethod
    def _add_damage(raider: Dict, result: Dict) -> Dict:
        if raider['actorType'] == 'TricksOfTheTrade':
            return result
        if raider['actorName'] in result:
            result[raider['actorName']] += raider['total']
        else:
            result[raider['actorName']] = raider['total']

        return result

    @staticmethod
    def _print_engineers(engineers: Dict, damage: Dict) -> str:
        if len(damage) == 0:
            return 'Вагонимся'

        damage = sorted(damage.items(), key=lambda item: item[1], reverse=True)

        value = ''
        for raider_name, raider_damage in damage:
            if len(value) > 980:
                return value
            if len(value) > 0:
                value += ', '

            value += raider_name
            value += '('
            value += str(raider_damage)
            value += ')'
            engineers = {key: val for key, val in engineers.items() if val != raider_name}

        if len(engineers) > 0:
            for _raider_id, raider_name in engineers.items():
                if len(value) > 980:
                    return value
                if len(value) > 0:
                    value += ', '

                value += raider_name
                value += '(0)'

        return value

    @staticmethod
    def _print_others(others: Dict) -> str:
        if len(others) == 0:
            return 'Не завезли'

        others = sorted(others.items(), key=lambda item: item[1], reverse=True)

        value = ''
        for raider_name, raider_damage in others:
            if len(value) > 980:
                return value
            if len(value) > 0:
                value += ', '

            value += raider_name
            value += '('
            value += str(raider_damage)
            value += ')'

        return value


def setup(bot):
    bot.add_cog(Bomberman(bot))
