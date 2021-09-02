import os
from datetime import datetime, timezone
from typing import Any, Dict, List

import discord
from discord import Colour, Embed, Message
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv

from config import settings
from constants import EXEC_VALUES, SPECS, ZONE_IMAGES, ZONE_NAMES
from wcl_client import WCLClient

load_dotenv()
bot = commands.Bot(command_prefix='slao.')


@bot.event
async def on_ready() -> None:
    print(f'We have logged in as {bot.user}')


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


@bot.command(name='msg', help='Get message by ID. Format: slao.msg SOME_MESSAGE_ID')
async def msg_command(ctx: Context, msg_id: int) -> None:
    msg = await ctx.fetch_message(msg_id)
    resp = msg.embeds[0].url.split('/')[-2]
    await ctx.send(resp)


@bot.command(name='wcl', help='Get data from report. Format: slao.wcl SOME_REPORT_ID')
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
    async with ctx.typing():
        wait_embed = Embed(
            description='Получаю данные с WarcraftLogs',
            colour=Colour.orange(),
        ).set_footer(text='Иногда WCL тормозит, пичалька.')
        waiting_embed = await ctx.send(embed=wait_embed)

        async with WCLClient() as client:
            result = await client.get_data(report_id)
        report_zone_id = result['reportData']['report']['zone']['id']

        report_title = ZONE_NAMES.get(report_zone_id, ZONE_NAMES.get(0))
        report_start = make_time(result['reportData']['report']['startTime'])
        report_end = make_time(result['reportData']['report']['endTime'])
        report_description = f'**Начало:** {report_start} \n **Окончание:** {report_end}'
        embed = Embed(title=report_title, description=report_description, color=0xb51cd4)

        report_owner = result['reportData']['report']['owner']['name']
        report_url = f'https://classic.warcraftlogs.com/reports/{report_id}'
        embed.set_author(name=report_owner, url=report_url, icon_url=author_icon)

        embed.set_image(url=ZONE_IMAGES.get(report_zone_id, ZONE_IMAGES.get(0)))

        fights = result['reportData']['report']['rankings']['data']
        if fights[-1]['fightID'] == 10000:
            make_total(embed, result)
        elif len(fights) <= 4:
            make_all_fights(embed, result)
        else:
            make_avg(embed, fights)
    await waiting_embed.edit(embed=embed)


def make_total(embed: Embed, rs: Dict[str, Any]) -> None:
    """
    Process total instance info only, not a per-boss info

    :param embed: :class:`discord.Embed` Embed to add fields to
    :param rs: :class:`dict' GraphQL request result
    :return:
    """

    rank = rs['reportData']['report']['rankings']['data'][-1]
    hps_rank = rs['reportData']['report']['hps']['data'][-1]

    embed.add_field(name='⚔️Полная зачистка', value=make_fight_info(rank), inline=False)
    embed.add_field(name='Танки', value=make_specs(rank['roles']['tanks']['characters']), inline=False)
    embed.add_field(name='Дамагеры', value=make_trophy_specs(rank['roles']['dps']['characters']), inline=False)
    embed.add_field(name='Лекари', value=make_trophy_specs(hps_rank['roles']['healers']['characters']), inline=False)


def make_all_fights(embed: discord.Embed, rs: Dict[str, Any]):
    """
    Process all fights from report

    :param embed: :class:`discord.Embed` Embed to add fields to
    :param rs: :class:`dict' GraphQL request result
    :return:
    """
    for fight_num, fight in enumerate(rs['reportData']['report']['rankings']['data']):
        embed.add_field(name='⚔️' + fight['encounter']['name'], value=make_fight_info(fight), inline=False)
        embed.add_field(name='Танки', value=make_specs(fight['roles']['tanks']['characters']), inline=False)
        embed.add_field(name='Дамагеры', value=make_trophy_specs(fight['roles']['dps']['characters']), inline=False)
        hps_rank = rs['reportData']['report']['hps']['data'][fight_num]['roles']['healers']['characters']
        embed.add_field(name='Лекари', value=make_trophy_specs(hps_rank), inline=False)


def make_avg(embed: Embed, fights: List[Dict[str, Any]]) -> None:
    bosses = ''
    execution = 0
    speed = 0
    for fight in fights:
        bosses += '⚔️**' + fight['encounter']['name'] + '** '
        execution += fight['execution']['rankPercent']
        speed += fight['speed']['rankPercent']

    embed.add_field(name='Убиты: ', value=bosses)
    execution = int(execution / len(fights))
    speed = int(speed / len(fights))

    value = f'Исполнение: **{make_execution(execution)}**\n'
    value += f'Скорость: **{speed}%**'
    embed.add_field(name='Рейтинг', value=value, inline=False)


def make_fight_info(fight: Dict[str, Any]) -> str:
    duration = datetime.fromtimestamp(fight['duration'] / 1000.0, timezone.utc).strftime('%Hч %Mм %Sс')
    value = f'Длительность: **{duration}**\n'
    value += f"Исполнение: **{make_execution(fight['execution']['rankPercent'])}**\n"
    value += f"Скорость: **{fight['speed']['rankPercent']}%**"
    return value


def make_specs(characters: List[Dict[str, Any]]) -> str:
    result = ''
    for char in characters:
        if len(result) > 980:
            return result
        key = char['class'] + '_' + char['spec']
        result += SPECS.get(key, '\u200b')
        result += '**' + char['name'] + '**  '
    return result


def make_trophy_specs(characters: List[Dict[str, Any]]) -> str:
    result = ''
    characters.sort(key=lambda x: x.get('rankPercent'), reverse=True)
    for place, char in enumerate(characters):
        if len(result) > 980:
            return result
        key = char['class'] + '_' + char['spec']
        if place < 3:
            result += '🏆 ' + SPECS.get(key, '\u200b') + '**' + char['name'] + '**  '
        else:
            result += SPECS.get(key, '\u200b') + char['name'] + '  '

    return result


def make_time(timestamp: int) -> str:
    utc_time = datetime.fromtimestamp(float(timestamp) / 1000, timezone.utc)
    local_time = utc_time.astimezone()
    return local_time.strftime('%Y-%m-%d %H:%M (%Z)')


def make_execution(percent: int) -> str:
    index = int((percent - 1) / 25)
    return EXEC_VALUES[index]


if __name__ == '__main__':
    bot.run(settings.discord_token)
