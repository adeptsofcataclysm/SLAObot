import os
import aiohttp

from dotenv import load_dotenv
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
                        ds.Report.exportedSegments,
                        ds.Report.zone.select(ds.Zone.name)
                    ))

                query = dsl_gql(DSLQuery(query_report))
                result = await cl.execute(query)

    response = result['reportData']['report']['zone']['name']
    await ctx.send(response)


bot.run(os.getenv('DISCORD_TOKEN'))
