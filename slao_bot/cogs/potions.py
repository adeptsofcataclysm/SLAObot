import discord
import tenacity
from discord import Colour, Embed, RawReactionActionEvent
from discord.ext import commands
from discord.ext.commands import Context
from slaobot import _delete_reply
from utils.constants import POT_IMAGES
from utils.report import Report
from utils.wcl_client import WCLClient


class Potions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        if payload.event_type != 'REACTION_ADD':
            return
        if payload.user_id == self.bot.user.id:
            return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message.author != self.bot.user:
            return
        if len(message.embeds) < 1:
            return

        if payload.emoji.name == '🧪':
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
        if payload.user_id == self.bot.user.id:
            return
        if payload.emoji.name == '🧪':
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if message.author != self.bot.user:
                return
            await _delete_reply(channel, message)

    @commands.command(name='pot')
    async def pot_command(self, ctx: Context, report_id: str) -> None:
        """Get data about potions used. Format: <prefix>pot SOME_REPORT_ID"""
        await self.process_pots(ctx, report_id)

    async def process_pots(self, ctx: Context, report_id: str) -> None:
        async with WCLClient() as client:
            try:
                rs = await client.get_pots(report_id)
            except tenacity.RetryError:
                return

        embed = Embed(title='Расходники', description='Пьём по КД, крутим ЕП!', colour=Colour.teal())
        embed.add_field(name=POT_IMAGES.get('mana'),
                        value=Report.get_pot_usage_sorted(rs['reportData']['report']['mana']['data']['entries']),
                        inline=False)

        embed.add_field(name=POT_IMAGES.get('hp'),
                        value=Report.get_pot_usage_sorted(rs['reportData']['report']['hp']['data']['entries']),
                        inline=False)

        embed.add_field(name=POT_IMAGES.get('hpmana'),
                        value=Report.get_pot_usage_sorted(rs['reportData']['report']['hpmana']['data']['entries']),
                        inline=False)

        embed.add_field(name=POT_IMAGES.get('manarunes'),
                        value=Report.get_pot_usage_sorted(rs['reportData']['report']['manarunes']['data']['entries']),
                        inline=False)

        embed.add_field(name=POT_IMAGES.get('drums'),
                        value=Report.get_pot_usage_sorted(rs['reportData']['report']['drums']['data']['entries']),
                        inline=False)

        embed.add_field(name=POT_IMAGES.get('herbs'),
                        value=Report.get_pot_usage_sorted(rs['reportData']['report']['herbs']['data']['entries']),
                        inline=False)

        embed.add_field(name=POT_IMAGES.get('combatpots'),
                        value=Report.get_pot_usage_sorted(rs['reportData']['report']['combatpots']['data']['entries']),
                        inline=False)

        await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(Potions(bot))
