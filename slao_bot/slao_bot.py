from typing import Any, Dict

import discord
import tenacity
from config import settings
from constants import ZONE_IMAGES
from discord import Colour, Embed, Message, Reaction
from discord.ext import commands
from discord.ext.commands import Context
from report import Report
from utils import bold, make_execution
from wcl_client import WCLClient

bot = commands.Bot(command_prefix=f'{settings.command_prefix}.')


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


@bot.event
async def on_reaction_add(reaction: Reaction, user) -> None:
    if user == bot.user:
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
        report_url = f'https://classic.warcraftlogs.com/reports/{report_id}'
        wait_embed = Embed(description='Получаю данные с WarcraftLogs', colour=Colour.orange(), url=report_url)
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

        fights = rs['reportData']['report']['rankings']['data']
        if fights[-1]['fightID'] == 10000:
            make_total(embed, rs)
        elif len(fights) <= 4:
            make_all_fights(embed, rs)
            await waiting_embed.add_reaction('🔄')
        else:
            make_avg(embed, rs)
            await waiting_embed.add_reaction('🔄')
    await waiting_embed.edit(embed=embed)


def make_total(embed: Embed, rs: Dict[str, Any]) -> None:
    """
    Process total instance info only, not a per-boss info

    :param embed: :class:`discord.Embed` Embed to add fields to
    :param rs: :class:`dict' GraphQL request result
    :return:
    """

    rank = rs['reportData']['report']['rankings']['data'][-1]

    embed.add_field(name='⚔️Полная зачистка', value=Report.make_fight_info(rank), inline=False)
    _add_specs(embed, rs, fight_num=-1)


def make_all_fights(embed: discord.Embed, rs: Dict[str, Any]):
    """
    Process all fights from report

    :param embed: :class:`discord.Embed` Embed to add fields to
    :param rs: :class:`dict' GraphQL request result
    :return:
    """
    for fight_num, fight in enumerate(rs['reportData']['report']['rankings']['data']):
        embed.add_field(name='⚔️' + fight['encounter']['name'], value=Report.make_fight_info(fight), inline=False)
        _add_specs(embed, rs, fight_num)


def _add_specs(embed: discord.Embed, rs: Dict[str, Any], fight_num: int) -> None:
    fight = rs['reportData']['report']['rankings']['data'][fight_num]

    embed.add_field(name='Танки', value=Report.make_spec(fight['roles']['tanks']['characters']), inline=False)
    embed.add_field(
        name='Дамагеры',
        value=Report.make_spec(fight['roles']['dps']['characters'], show_trophy=True),
        inline=False,
    )

    hps_rank = rs['reportData']['report']['hps']['data'][fight_num]['roles']['healers']['characters']
    embed.add_field(
        name='Лекари',
        value=Report.make_spec(hps_rank, show_trophy=True),
        inline=False,
    )


def make_avg(embed: Embed, result: Dict[str, Any]) -> None:
    bosses = ''
    execution = 0
    speed = 0
    tank = []
    damage = []
    heal = []
    fights = result['reportData']['report']['rankings']['data']
    for fight in fights:
        bosses += f"⚔{bold(fight['encounter']['name'])} "
        execution += fight['execution']['rankPercent']
        speed += fight['speed']['rankPercent']
        Report.sum_rank(tank, fight['roles']['tanks']['characters'])
        Report.sum_rank(damage, fight['roles']['dps']['characters'])

    for char in tank:
        char['rankPercent'] = int(char['rankPercent'] / char['fightsAmount'])

    for char in damage:
        char['rankPercent'] = int(char['rankPercent'] / char['fightsAmount'])

    fights = result['reportData']['report']['hps']['data']
    for fight in fights:
        Report.sum_rank(heal, fight['roles']['healers']['characters'])

    for char in heal:
        char['rankPercent'] = int(char['rankPercent'] / char['fightsAmount'])

    embed.add_field(name='Убиты: ', value=bosses)

    execution = int(execution / len(fights))
    speed = int(speed / len(fights))
    value = f'Исполнение: {bold(make_execution(execution))}\n'
    value += f'Скорость: {bold(speed)}%'
    embed.add_field(name='Рейтинг', value=value, inline=False)
    embed.add_field(name='Танки', value=Report.make_spec(tank), inline=False)
    embed.add_field(name='Дамагеры', value=Report.make_spec(damage, show_trophy=True), inline=False)
    embed.add_field(name='Лекари', value=Report.make_spec(heal, show_trophy=True), inline=False)


if __name__ == '__main__':
    bot.run(settings.discord_token)
