from typing import Any, Dict

import aiohttp
import tenacity
from diskcache import Cache
from gql import Client
from gql.client import AsyncClientSession
from gql.dsl import DSLQuery, DSLSchema, dsl_gql
from gql.transport.aiohttp import AIOHTTPTransport
from utils.config import settings


class WCLClient:

    _client: Client
    _session: AsyncClientSession
    _cache: Cache

    async def __aenter__(self) -> 'WCLClient':
        async with aiohttp.ClientSession() as cs:
            data = {'grant_type': 'client_credentials'}
            auth_header = aiohttp.BasicAuth(settings.wcl_client_id, settings.wcl_client_secret)
            async with cs.post('https://www.warcraftlogs.com/oauth/token', data=data, auth=auth_header) as auth:
                res = await auth.json()
                wcl_token = res['access_token']

        transport = AIOHTTPTransport(
            url='https://www.warcraftlogs.com/api/v2/client',
            headers={'Authorization': f'Bearer {wcl_token}'},
        )
        self._client = Client(transport=transport, fetch_schema_from_transport=True)
        self._session = await self._client.__aenter__()
        self._cache = Cache('cache')

        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self._client.__aexit__(exc_type, exc_val, exc_tb)

    @tenacity.retry(wait=tenacity.wait_exponential(), stop=tenacity.stop_after_delay(120))
    async def get_data(self, report_id: str) -> Dict[str, Any]:
        """
        Gets data from WarcraftLog.

        :param report_id: :class:`str` WarcraftLogs report ID.
        :return: GraphQL request result. Should be a JSON based dictionary object.
        """
        ds = DSLSchema(self._client.schema)

        query_report = ds.Query.reportData

        query_report.select(
            ds.ReportData.report(code=report_id).select(
                ds.Report.startTime,
                ds.Report.endTime,
                ds.Report.zone.select(ds.Zone.name),
            ))
        query = dsl_gql(DSLQuery(query_report))
        result = await self._session.execute(query)

        if result['reportData']['report']['zone']['name'] is None:
            raise Exception('Zone name not found')

        cached_report = self._cache.get('report_id')
        if (cached_report
                and cached_report['reportData']['report']['endTime'] == result['reportData']['report']['endTime']):
            return cached_report

        end_time = result['reportData']['report']['endTime'] - result['reportData']['report']['startTime']

        query_report.select(
            ds.ReportData.report(code=report_id).select(
                ds.Report.startTime,
                ds.Report.endTime,
                ds.Report.owner.select(ds.User.name),
                ds.Report.zone.select(ds.Zone.id),
                ds.Report.zone.select(ds.Zone.name),
                ds.Report.zone.select(ds.Zone.frozen),
                ds.Report.rankings(compare='Rankings'),
                ds.Report.table(dataType='Summary', startTime=0, endTime=end_time),
            ))

        query = dsl_gql(DSLQuery(query_report))
        result = await self._session.execute(query)
        self._cache.set('report_id', result)

        return result

    @tenacity.retry(wait=tenacity.wait_exponential(), stop=tenacity.stop_after_delay(120))
    async def get_pots(self, report_id: str) -> Dict[str, Any]:
        """
        Gets data about potions used from WarcraftLog.

        :param report_id: :class:`str` WarcraftLogs report ID.
        :return: GraphQL request result. Should be a JSON based dictionary object.
        """

        ds = DSLSchema(self._client.schema)

        query_report = ds.Query.reportData

        query_report.select(
            ds.ReportData.report(code=report_id).select(
                ds.Report.startTime,
                ds.Report.endTime,
                ds.Report.zone.select(ds.Zone.name),
            ))
        query = dsl_gql(DSLQuery(query_report))
        result = await self._session.execute(query)

        if result['reportData']['report']['zone']['name'] is None:
            raise Exception('Zone name not found')

        end_time = result['reportData']['report']['endTime'] - result['reportData']['report']['startTime']

        query_report.select(
            ds.ReportData.report(code=report_id).select(
                mana=ds.Report.table(
                    dataType='Casts',
                    startTime=0,
                    endTime=end_time,
                    filterExpression='ability.id in (43186, 67490)'),
                hp=ds.Report.table(
                    dataType='Casts',
                    startTime=0,
                    endTime=end_time,
                    filterExpression='ability.id in (43185, 67489)'),
                hpmana=ds.Report.table(
                    dataType='Casts',
                    startTime=0,
                    endTime=end_time,
                    filterExpression='ability.id in (53750, 53761)'),
                manarunes=ds.Report.table(
                    dataType='Casts',
                    startTime=0,
                    endTime=end_time,
                    filterExpression='ability.id in (16666, 27869)'),
                combatpots=ds.Report.table(
                    dataType='Casts',
                    startTime=0,
                    endTime=end_time,
                    filterExpression='ability.id in (53908, 53909, 53762)'),
            ))

        query = dsl_gql(DSLQuery(query_report))
        result = await self._session.execute(query)

        return result

    @tenacity.retry(wait=tenacity.wait_exponential(), stop=tenacity.stop_after_delay(120))
    async def get_gear(self, report_id: str) -> Dict[str, Any]:
        """
        Gets data about gear used from WarcraftLog.

        :param report_id: :class:`str` WarcraftLogs report ID.
        :return: GraphQL request result. Should be a JSON based dictionary object.
        """

        ds = DSLSchema(self._client.schema)
        query_report = ds.Query.reportData

        query_report.select(
            ds.ReportData.report(code=report_id).select(
                ds.Report.startTime,
                ds.Report.endTime,
                ds.Report.zone.select(ds.Zone.name),
            ))

        query = dsl_gql(DSLQuery(query_report))
        result = await self._session.execute(query)

        if result['reportData']['report']['zone']['name'] is None:
            raise Exception('Zone name not found')

        end_time = result['reportData']['report']['endTime'] - result['reportData']['report']['startTime']

        query_report.select(
            ds.ReportData.report(code=report_id).select(
                ds.Report.startTime,
                ds.Report.endTime,
                ds.Report.table(dataType='Summary', startTime=0, endTime=end_time),
            ))

        query = dsl_gql(DSLQuery(query_report))
        result = await self._session.execute(query)

        return result
