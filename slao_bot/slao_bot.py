from typing import Any, Dict

import discord
import tenacity
from discord import Colour, Embed, Message, Reaction
from discord.ext import commands
from discord.ext.commands import Context
from config import settings
from constants import ZONE_IMAGES, Role
from report import Report
from utils import bold, make_execution
from wcl_client import WCLClient

bot = commands.Bot(command_prefix=f'{settings.command_prefix}')


@bot.event
async def on_ready() -> None:
    print(f'We have logged in as {bot.user}')
    print(f'Command prefix is: {bot.command_prefix}')


@bot.event
async def on_message(message: Message) -> None:
    await bot.process_commands(message)
    if message.author == bot.user:
        return

    if message.author.display_name == 'WCL' and message.embeds:
        report_id = message.embeds[0].url.split('/')[-2]
        author_icon = message.embeds[0].thumbnail.url
        if report_id:
            ctx = await bot.get_context(message)
            await process_report(ctx, report_id, author_icon)


@bot.event
async def on_reaction_add(reaction: Reaction, user) -> None:
    if user == bot.user:
        return
    if reaction.message.author != bot.user:
        return
    if reaction.emoji != '🔄':
        return
    if reaction.message.embeds[0].url:
        # Waiting Embed
        report_id = reaction.message.embeds[0].url.split('/')[-1]
        author_icon = reaction.message.embeds[0].thumbnail.url
    else:
        # Rankings embed
        report_id = reaction.message.embeds[0].author.url.split('/')[-1]
        author_icon = reaction.message.embeds[0].author.icon_url

    ctx = await bot.get_context(reaction.message)
    await reaction.message.delete()
    await process_report(ctx, report_id, author_icon)


@bot.command(name='msg', help='Get message by ID. Format: <prefix>msg SOME_MESSAGE_ID')
async def msg_command(ctx: Context, msg_id: int) -> None:
    msg = await ctx.fetch_message(msg_id)
    resp = msg.embeds[0].url.split('/')[-2]
    await ctx.send(resp)


@bot.command(name='wcl', aliases=['🍦'], help='Get data from report. Format: <prefix>лог SOME_REPORT_ID')
async def wcl_command(ctx: Context, report_id: str) -> None:
    author_icon = 'https://cdn.discordapp.com/icons/620682853709250560/6c53810d8a4e2b75069208a472465694.png'
    await process_report(ctx, report_id, author_icon)


async def process_report(ctx: Context, report_id: str, author_icon: str) -> None:
    """
    Process a single report and sends embed to context channel

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
    # Delete original WCL message
    if ctx.message.embeds and ctx.message.author != bot.user:
        await ctx.message.delete()

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
        await _make_fights(rs, embed, waiting_embed)

    # Print raiders
    _make_raiders(embed, rs)

    await waiting_embed.edit(embed=embed)


async def _make_fights(rs: Dict[str, Any], embed: Embed, waiting_embed: Message) -> None:
    fights = rs['reportData']['report']['rankings']['data']

    if len(fights) == 0:
        embed.add_field(name='Лог пустой', value='Пора побеждать боссов!', inline=False)
        await waiting_embed.add_reaction('🔄')
        return

    if fights[-1]['fightID'] == 10000:
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
        embed.add_field(name=bosses, value=value, inline=False)
        await waiting_embed.add_reaction('🔄')


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


if __name__ == '__main__':
    bot.run(settings.discord_token)
