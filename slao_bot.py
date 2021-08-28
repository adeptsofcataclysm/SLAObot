import os
import aiohttp
import discord
import tenacity

from dotenv import load_dotenv
from datetime import datetime, timezone
from discord.ext import commands
from gql import Client
from gql.dsl import DSLQuery, DSLSchema, dsl_gql
from gql.transport.aiohttp import AIOHTTPTransport

load_dotenv()
bot = commands.Bot(command_prefix='slao.')
specs = {
    "Druid_Balance": "<:Druid_Balance:880098174985961542>",
    "Druid_Feral": "<:Druid_Feral:880098483636408392>",
    "Druid_Guardian": "<:druid_guardian:880068396803297311>",
    "Druid_Restoration": "<:Druid_Restoration:880089474753785897>",
    "Druid_Warden": "<:Druid_Warden:880081285501046854>",
    "Hunter_BeastMastery": "<:Hunter_BeastMastery:880083922120233030>",
    "Mage_Arcane": "<:Mage_Arcane:880098759936196669>",
    "Mage_Fire": "<:Mage_Fire:880083302306947113>",
    "Paladin_Holy": "<:Paladin_Holy:880089741847060550>",
    "Paladin_Protection": "<:Paladin_Protection:880076303615787009>",
    "Paladin_Retribution": "<:Paladin_Retribution:880099271645470750>",
    "Priest_Discipline": "<:Priest_Discipline:880089778551414824>",
    "Priest_Holy": "<:Priest_Holy:880089805990535169>",
    "Priest_Shadow": "<:Priest_Shadow:880099152548208731>",
    "Priest_Smiter": "<:Priest_Smiter:880085315149258848>",
    "Rogue_Combat": "<:Rogue_Combat:880082256373370891>",
    "Shaman_Elemental": "<:Shaman_Elemental:880084253700923412>",
    "Shaman_Enhancement": "<:Shaman_Enhancement:880082514683756615>",
    "Shaman_Restoration": "<:Shaman_Restoration:880099191706247208>",
    "Warlock_Affliction": "<:Warlock_Affliction:880099108369612801>",
    "Warlock_Demonology": "<:Warlock_Demonology:880090452949336125>",
    "Warlock_Destruction": "<:Warlock_Destruction:880085124606210109>",
    "Warrior_Arms": "<:Warrior_Arms:880084581901025340>",
    "Warrior_Fury": "<:Warrior_Fury:880084813376286762>",
    "Warrior_Protection": "<:Warrior_Protection:880080701930733638>"
}

zone_images = {
    1007: "https://cdn.discordapp.com/attachments/762790105026920468/843540146379948042/RH-TBC-Karazhan1-1200x300.png",
    1008: "https://cdn.discordapp.com/attachments/762790105026920468/876774093943349258/RH-TBC-GruulMaggie_1200x300.png",
    0: "https://cdn.discordapp.com/attachments/762790105026920468/843540093422796810/RH-TBC-DarkPortal1-1200x300.png"
}

exec_values = {
    0: "Слабо",
    1: "На троечку",
    2: "Крутим гайки",
    3: "МоЩЩно"
}


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return

    if message.author.display_name == "WCL" and message.embeds:
        report_id = message.embeds[0].url.split("/")[-2]
        if report_id:
            ctx = await bot.get_context(message)
            await process_report(ctx, report_id)


@bot.command(name="msg", help='Get message by ID. Format: slao.msg SOME_MESSAGE_ID')
async def msg_command(ctx, msg_id):
    msg = await ctx.fetch_message(msg_id)
    resp = msg.embeds[0].url.split("/")[-2]
    await ctx.send(resp)


@bot.command(name='wcl', help='Get data from report. Format: slao.wcl SOME_REPORT_ID')
async def wcl_command(ctx, report_id):
    await process_report(ctx, report_id)


async def process_report(ctx, report_id):
    """
    Process a single report and sends embed to context channel

    :param ctx: Invocation context. Should be a channel
    :param report_id: :class:`str` WarcraftLogs report ID
    :return:
    """
    async with ctx.typing():
        wait_embed = discord \
            .Embed(description="Получаю данные с WarcraftLogs", colour=discord.Colour.orange()) \
            .set_footer(text="Иногда WCL тормозит, пичалька.")
        waiting_embed = await ctx.send(embed=wait_embed)

        result = await get_data(report_id)
        report_title = result['reportData']['report']['zone']['name']
        report_owner = result['reportData']['report']['owner']['name']
        report_start = make_time(result['reportData']['report']['startTime'])
        report_end = make_time(result['reportData']['report']['endTime'])
        report_zone_id = result['reportData']['report']['zone']['id']

        embed = discord.Embed(title=report_title, description=f"Лог от {report_owner}", color=0x6b6b6b)
        embed.add_field(name="Начало", value=report_start, inline=True)
        embed.add_field(name="Окончание", value=report_end, inline=True)
        # blank 3rd column
        embed.add_field(name="\u200b", value="\u200b", inline=True)

        # Gruul + Magtheridon
        if report_zone_id == 1008:
            make_1008(embed, result)
        # Full Karazhan
        elif report_zone_id == 1007:
            # TO-DO Add check for full Kara
            make_1502(embed, result['reportData']['report']['rankings']['data'][-1])

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
        async with cs.post("https://www.warcraftlogs.com/oauth/token", data=data, auth=auth_header) as auth:
            res = await auth.json()
            wcl_token = res['access_token']
            transport = AIOHTTPTransport(
                url="https://www.warcraftlogs.com/api/v2/client", headers={'Authorization': f"Bearer {wcl_token}"}
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
                        ds.Report.rankings(compare="Rankings")
                    ))

                query = dsl_gql(DSLQuery(query_report))
                result = await cl.execute(query)
                if result['reportData']['report']['zone']['name'] is None:
                    raise
                if len(result['reportData']['report']['rankings']['data']) == 0:
                    raise
                return result


# Add data for full Karazhan
def make_1502(embed: discord.Embed, rs: dict):
    embed.set_image(url=zone_images.get(1007))
    embed.add_field(name="Полная зачистка", value=make_fight_info(rs), inline=False)
    embed.add_field(name="Tank", value=make_specs(rs['roles']['tanks']['characters']), inline=False)
    embed.add_field(name="DPS", value=make_specs(rs['roles']['dps']['characters']), inline=False)
    embed.add_field(name="Heal", value=make_specs(rs['roles']['healers']['characters']), inline=False)


# Add data for Gruul + Magtheridon
def make_1008(embed: discord.Embed, rs: dict):
    embed.set_image(url=zone_images.get(1008))
    for fight in rs['reportData']['report']['rankings']['data']:
        embed.add_field(name=fight['encounter']['name'], value=make_fight_info(fight), inline=False)
        embed.add_field(name="Танк", value=make_specs(fight['roles']['tanks']['characters']), inline=False)
        embed.add_field(name="Дамагеры", value=make_specs(fight['roles']['dps']['characters']), inline=False)
        embed.add_field(name="Лекари", value=make_specs(fight['roles']['healers']['characters']), inline=False)


def make_fight_info(fight: dict):
    val = "Длительность: **{}**\n" \
        .format(datetime.fromtimestamp(fight['duration'] / 1000.0, timezone.utc).strftime('%Hч %Mм %Sс'))
    val += "Исполнение: **{}**\n".format(make_execution(fight['execution']['rankPercent']))
    val += "Скорость: **{}%**".format(fight['speed']['rankPercent'])
    return val


def make_specs(rs: dict):
    result = ""
    for char in rs:
        key = char['class'] + "_" + char['spec']
        result += specs.get(key, "\u200b")
        result += "**" + char['name'] + "**  "
    return result


def make_time(timestamp: int):
    utc_time = datetime.fromtimestamp(float(timestamp) / 1000, timezone.utc)
    local_time = utc_time.astimezone()
    return local_time.strftime("%Y-%m-%d %H:%M (%Z)")


def make_execution(percent: int):
    if 25 < percent <= 50:
        return exec_values[1]
    elif 50 < percent <= 75:
        return exec_values[2]
    elif percent > 75:
        return exec_values[3]

    return exec_values[0]


bot.run(os.getenv('DISCORD_TOKEN'))
