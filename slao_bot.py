import os
from datetime import datetime, timezone

import aiohttp
import discord
import tenacity
from discord.ext import commands
from dotenv import load_dotenv
from gql import Client
from gql.dsl import DSLQuery, DSLSchema, dsl_gql
from gql.transport.aiohttp import AIOHTTPTransport

load_dotenv()
bot = commands.Bot(command_prefix='slao.')
SPECS = {
    'Druid_Balance': '<:Druid_Balance:880098174985961542>',
    'Druid_Feral': '<:Druid_Feral:880098483636408392>',
    'Druid_Guardian': '<:druid_guardian:880068396803297311>',
    'Druid_Restoration': '<:Druid_Restoration:880089474753785897>',
    'Druid_Warden': '<:Druid_Warden:880081285501046854>',
    'Hunter_BeastMastery': '<:Hunter_BeastMastery:880083922120233030>',
    'Hunter_Marksmanship': '<:Hunter_Marksmanship:881622924564516934>',
    'Mage_Arcane': '<:Mage_Arcane:880098759936196669>',
    'Mage_Fire': '<:Mage_Fire:880083302306947113>',
    'Mage_Frost': '<:Mage_Frost:881623228177596437>',
    'Paladin_Holy': '<:Paladin_Holy:880089741847060550>',
    'Paladin_Protection': '<:Paladin_Protection:880076303615787009>',
    'Paladin_Retribution': '<:Paladin_Retribution:880099271645470750>',
    'Priest_Discipline': '<:Priest_Discipline:880089778551414824>',
    'Priest_Holy': '<:Priest_Holy:880089805990535169>',
    'Priest_Shadow': '<:Priest_Shadow:880099152548208731>',
    'Priest_Smiter': '<:Priest_Smiter:880085315149258848>',
    'Rogue_Assassination': '<:Rogue_Assassination:881623680025780245>',
    'Rogue_Combat': '<:Rogue_Combat:880082256373370891>',
    'Shaman_Elemental': '<:Shaman_Elemental:880084253700923412>',
    'Shaman_Enhancement': '<:Shaman_Enhancement:880082514683756615>',
    'Shaman_Restoration': '<:Shaman_Restoration:880099191706247208>',
    'Warlock_Affliction': '<:Warlock_Affliction:880099108369612801>',
    'Warlock_Demonology': '<:Warlock_Demonology:880090452949336125>',
    'Warlock_Destruction': '<:Warlock_Destruction:880085124606210109>',
    'Warrior_Arms': '<:Warrior_Arms:880084581901025340>',
    'Warrior_Fury': '<:Warrior_Fury:880084813376286762>',
    'Warrior_Protection': '<:Warrior_Protection:880080701930733638>',
}

ZONE_IMAGES = {
    1000: 'https://cdn.discordapp.com/attachments/762790105026920468/762790308844273714/image0.jpg',
    1007: 'https://cdn.discordapp.com/attachments/762790105026920468/843540146379948042/RH-TBC-Karazhan1-1200x300.png',
    1008: 'https://cdn.discordapp.com/attachments/762790105026920468/'
          '876774093943349258/RH-TBC-GruulMaggie_1200x300.png',
    0: 'https://cdn.discordapp.com/attachments/762790105026920468/843540093422796810/RH-TBC-DarkPortal1-1200x300.png',
}

ZONE_NAMES = {
    0: ':regional_indicator_r: :regional_indicator_a: :id:',
    1000: 'MC',
    1007: ':regional_indicator_k: :regional_indicator_a: :regional_indicator_r: :regional_indicator_a: '
          ':regional_indicator_z: :regional_indicator_h: :regional_indicator_a: :regional_indicator_n:',
    1008: ':regional_indicator_g: :regional_indicator_r: :regional_indicator_u: :regional_indicator_u: '
          ':regional_indicator_l: :left_right_arrow: :regional_indicator_m: :regional_indicator_a: '
          ':regional_indicator_g: :regional_indicator_a:',
}

EXEC_VALUES = {
    0: 'Слабо',
    1: 'На троечку',
    2: 'Крутим гайки',
    3: 'МоЩЩно',
}


@bot.event
async def on_ready() -> None:
    print(f'We have logged in as {bot.user}')


@bot.event
async def on_message(message) -> None:
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
async def msg_command(ctx, msg_id):
    msg = await ctx.fetch_message(msg_id)
    resp = msg.embeds[0].url.split('/')[-2]
    await ctx.send(resp)


@bot.command(name='wcl', help='Get data from report. Format: slao.wcl SOME_REPORT_ID')
async def wcl_command(ctx, report_id):
    author_icon = 'https://cdn.discordapp.com/icons/620682853709250560/6c53810d8a4e2b75069208a472465694.png'
    await process_report(ctx, report_id, author_icon)


async def process_report(ctx, report_id, author_icon):
    """
    Process a single report and sends embed to context channel

    :param author_icon:
    :param ctx: Invocation context. Should be a channel
    :param report_id: :class:`str` WarcraftLogs report ID
    :return:
    """
    async with ctx.typing():
        wait_embed = discord.Embed(
            description='Получаю данные с WarcraftLogs',
            colour=discord.Colour.orange(),
        ).set_footer(text='Иногда WCL тормозит, пичалька.')
        waiting_embed = await ctx.send(embed=wait_embed)

        result = await get_data(report_id)
        report_zone_id = result['reportData']['report']['zone']['id']

        report_title = ZONE_NAMES.get(report_zone_id, ZONE_NAMES.get(0))
        report_start = make_time(result['reportData']['report']['startTime'])
        report_end = make_time(result['reportData']['report']['endTime'])
        report_description = f'**Начало:** {report_start} \n **Окончание:** {report_end}'
        embed = discord.Embed(title=report_title, description=report_description, color=0xb51cd4)

        report_owner = result['reportData']['report']['owner']['name']
        report_url = f'https://classic.warcraftlogs.com/reports/{report_id}'
        embed.set_author(name=report_owner, url=report_url, icon_url=author_icon)

        embed.set_image(url=ZONE_IMAGES.get(report_zone_id, ZONE_IMAGES.get(0)))

        fights = result['reportData']['report']['rankings']['data']
        if fights[-1]['fightID'] == 10000:
            make_total(embed, fights[-1])
        elif len(fights) <= 4:
            make_all_fights(embed, fights)
        else:
            make_avg(embed, fights)
    await waiting_embed.edit(embed=embed)


@tenacity.retry(wait=tenacity.wait_exponential(), stop=tenacity.stop_after_delay(120))
async def get_data(report_id):
    """
    Gets data from WarcraftLog.
    Authentication token requested as a first call. With logs posted on daily or semi-daily basis
    and not every minute it is fine to request it each time we make a call to WCL

    :param report_id: :class:`str` WarcraftLogs report ID.
    :return: GraphQL request result. Should be a JSON based dictionary object.
    """
    async with aiohttp.ClientSession() as cs:
        data = {'grant_type': 'client_credentials'}
        auth_header = aiohttp.BasicAuth(os.getenv('WCL_CLIENT_ID'), os.getenv('WCL_CLIENT_SECRET'))
        async with cs.post('https://www.warcraftlogs.com/oauth/token', data=data, auth=auth_header) as auth:
            res = await auth.json()
            wcl_token = res['access_token']
            transport = AIOHTTPTransport(
                url='https://www.warcraftlogs.com/api/v2/client',
                headers={'Authorization': f'Bearer {wcl_token}'},
            )
            wcl_client = Client(transport=transport, fetch_schema_from_transport=True)
            async with wcl_client as cl:
                ds = DSLSchema(wcl_client.schema)

                query_report = ds.Query.reportData

                query_report.select(
                    ds.ReportData.report(code=report_id).select(
                        ds.Report.startTime,
                        ds.Report.endTime,
                        ds.Report.owner.select(ds.User.name),
                        ds.Report.exportedSegments,
                        ds.Report.zone.select(ds.Zone.id),
                        ds.Report.zone.select(ds.Zone.name),
                        ds.Report.rankings(compare='Rankings'),
                    ))

                query = dsl_gql(DSLQuery(query_report))
                result = await cl.execute(query)
                if result['reportData']['report']['zone']['name'] is None:
                    raise
                if len(result['reportData']['report']['rankings']['data']) == 0:
                    raise
                return result


def make_total(embed: discord.Embed, rs: dict):
    """
    Process total instance info only, not a per-boss info

    :param embed: :class:`discord.Embed` Embed to add fields to
    :param rs: :class:`dict' Dictionary with characters
    :return:
    """
    embed.add_field(name='⚔️Полная зачистка', value=make_fight_info(rs), inline=False)
    embed.add_field(name='Танки', value=make_specs(rs['roles']['tanks']['characters']), inline=False)
    embed.add_field(name='Дамагеры', value=make_trophy_specs(rs['roles']['dps']['characters']), inline=False)
    embed.add_field(name='Лекари', value=make_specs(rs['roles']['healers']['characters']), inline=False)


def make_all_fights(embed: discord.Embed, rs: dict):
    """
    Process all fights from report

    :param embed: :class:`discord.Embed` Embed to add fields to
    :param rs: :class:`dict' Dictionary with characters
    :return:
    """
    for fight in rs:
        embed.add_field(name='⚔️' + fight['encounter']['name'], value=make_fight_info(fight), inline=False)
        embed.add_field(name='Танки', value=make_specs(fight['roles']['tanks']['characters']), inline=False)
        embed.add_field(name='Дамагеры', value=make_trophy_specs(fight['roles']['dps']['characters']), inline=False)
        embed.add_field(name='Лекари', value=make_specs(fight['roles']['healers']['characters']), inline=False)


def make_avg(embed: discord.Embed, rs: list):
    bosses = ''
    execution = 0
    speed = 0
    for fight in rs:
        bosses += '⚔️**' + fight['encounter']['name'] + '** '
        execution += fight['execution']['rankPercent']
        speed += fight['speed']['rankPercent']

    embed.add_field(name='Убиты: ', value=bosses)
    execution = int(execution / len(rs))
    speed = int(speed / len(rs))

    value = f'Исполнение: **{make_execution(execution)}**\n'
    value += f'Скорость: **{speed}%**'
    embed.add_field(name='Рейтинг', value=value, inline=False)


def make_fight_info(fight: dict):
    duration = datetime.fromtimestamp(fight['duration'] / 1000.0, timezone.utc).strftime('%Hч %Mм %Sс')
    value = f'Длительность: **{duration}**\n'
    value += f"Исполнение: **{make_execution(fight['execution']['rankPercent'])}**\n"
    value += f"Скорость: **{fight['speed']['rankPercent']}%**"
    return value


def make_specs(rs: list):
    result = ''
    for char in rs:
        if len(result) > 980:
            return result
        key = char['class'] + '_' + char['spec']
        result += SPECS.get(key, '\u200b')
        result += '**' + char['name'] + '**  '
    return result


def make_trophy_specs(rs: list):
    result = ''
    rs.sort(key=lambda x: x.get('rankPercent'), reverse=True)
    for place, char in enumerate(rs):
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


bot.run(os.getenv('DISCORD_TOKEN'))
