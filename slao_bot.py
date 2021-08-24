import os
import aiohttp
import discord
import asyncio

from dotenv import load_dotenv
from datetime import datetime, timezone
from discord.ext import commands
from gql import Client
from gql.dsl import DSLQuery, DSLSchema, dsl_gql
from gql.transport.aiohttp import AIOHTTPTransport

load_dotenv()
bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.command(name='wcl', help='Get data from report. Format: !wcl SOME_REPORT_ID')
async def get_data(ctx, report_id):
    async with ctx.typing():
        await asyncio.sleep(5)

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
                        ds.Report.zone.select(ds.Zone.name)
                    ))

                query = dsl_gql(DSLQuery(query_report))
                result = await cl.execute(query)

    report_title = result['reportData']['report']['zone']['name']
    report_owner = result['reportData']['report']['owner']['name']
    report_start = make_time(result['reportData']['report']['startTime'])
    report_end = make_time(result['reportData']['report']['endTime'])

    embed = discord.Embed(title=report_title, description=f"Reported by {report_owner}", color=0x6b6b6b)
    embed.add_field(name="Start time", value=report_start, inline=True)
    embed.add_field(name="End time", value=report_end, inline=True)

    await ctx.send(embed=embed)


def make_time(timestamp: int):
    utc_time = datetime.fromtimestamp(float(timestamp)/1000, timezone.utc)
    local_time = utc_time.astimezone()
    return local_time.strftime("%Y-%m-%d %H:%M (%Z)")


bot.run(os.getenv('DISCORD_TOKEN'))
