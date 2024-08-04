from typing import Any, Dict, Optional

import aiohttp
import tenacity
import utils.constants
import utils.engineer
from diskcache import Cache
from gql import Client
from gql.client import AsyncClientSession
from gql.dsl import DSLQuery, DSLSchema, dsl_gql
from gql.transport.aiohttp import AIOHTTPTransport
from utils.config import base_config


class WCLClient:
    _client: Client
    _session: AsyncClientSession
    _cache: Cache
    _schema: DSLSchema

    async def __aenter__(self) -> 'WCLClient':
        async with aiohttp.ClientSession() as cs:
            data = {'grant_type': 'client_credentials'}
            auth_header = aiohttp.BasicAuth(base_config['BASE']['WCL_CLIENT_ID'],
                                            base_config['BASE']['WCL_CLIENT_SECRET'])
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
        self._schema = DSLSchema(self._client.schema)

        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self._client.__aexit__(exc_type, exc_val, exc_tb)

    @tenacity.retry(wait=tenacity.wait_exponential(), stop=tenacity.stop_after_delay(120))
    async def get_rankings(self, report_id: str) -> Dict[str, Any]:
        """
        Gets data from WarcraftLog.

        :param report_id: :class:`str` WarcraftLogs report ID.
        :return: GraphQL request result. Should be a JSON based dictionary object.
        """

        result = await self.get_report_times(report_id)
        cached_report = self.get_cache(report_id, result['reportData']['report']['endTime'])
        if cached_report:
            return cached_report

        query_report = self._schema.Query.reportData

        query_report.select(
            self._schema.ReportData.report(code=report_id).select(
                self._schema.Report.startTime,
                self._schema.Report.endTime,
                self._schema.Report.owner.select(self._schema.User.name),
                self._schema.Report.title,
                self._schema.Report.guildTag.select(self._schema.GuildTag.name),
                self._schema.Report.zone.select(self._schema.Zone.id),
                self._schema.Report.zone.select(self._schema.Zone.name),
                self._schema.Report.zone.select(self._schema.Zone.frozen),
                self._schema.Report.rankings(compare='Rankings'),
            ))

        query = dsl_gql(DSLQuery(query_report))
        result = await self._session.execute(query)
        self._cache.set(report_id, result)

        return result

    @tenacity.retry(wait=tenacity.wait_exponential(), stop=tenacity.stop_after_delay(120))
    async def get_pots(self, report_id: str) -> Dict[str, Any]:
        """
        Gets data about potions used from WarcraftLog.

        :param report_id: :class:`str` WarcraftLogs report ID.
        :return: GraphQL request result. Should be a JSON based dictionary object.
        """

        result = await self.get_report_times(report_id)
        cached_report = self.get_cache('pots_' + report_id, result['reportData']['report']['endTime'])
        if cached_report:
            return cached_report

        end_time = result['reportData']['report']['endTime'] - result['reportData']['report']['startTime']

        hp_mana_pots = ','.join(utils.constants.HP_MANA_POTS)
        hp_mana_stones = ','.join(utils.constants.HP_MANA_STONES)
        combat_pots = ','.join(utils.constants.COMBAT_POTS)

        query_report = self._schema.Query.reportData

        query_report.select(
            self._schema.ReportData.report(code=report_id).select(
                self._schema.Report.startTime,
                self._schema.Report.endTime,
                hp_mana_pots=self._schema.Report.table(
                    dataType='Casts',
                    startTime=0,
                    endTime=end_time,
                    filterExpression=f'ability.ID in ({hp_mana_pots})'),
                hp_mana_stones=self._schema.Report.table(
                    dataType='Casts',
                    startTime=0,
                    endTime=end_time,
                    filterExpression=f'ability.ID in ({hp_mana_stones})'),
                combat_pots=self._schema.Report.table(
                    dataType='Casts',
                    startTime=0,
                    endTime=end_time,
                    filterExpression=f'ability.ID in ({combat_pots})'),
            ))

        query = dsl_gql(DSLQuery(query_report))
        result = await self._session.execute(query)
        self._cache.set('pots_' + report_id, result)

        return result

    @tenacity.retry(wait=tenacity.wait_exponential(), stop=tenacity.stop_after_delay(120))
    async def get_table_summary(self, report_id: str) -> Dict[str, Any]:
        """
        Gets data about gear used from WarcraftLog.

        :param report_id: :class:`str` WarcraftLogs report ID.
        :return: GraphQL request result. Should be a JSON based dictionary object.
        """
        result = await self.get_report_times(report_id)
        cached_report = self.get_cache('gear_' + report_id, result['reportData']['report']['endTime'])
        if cached_report:
            return cached_report

        end_time = result['reportData']['report']['endTime'] - result['reportData']['report']['startTime']

        query_report = self._schema.Query.reportData
        query_report.select(
            self._schema.ReportData.report(code=report_id).select(
                self._schema.Report.startTime,
                self._schema.Report.endTime,
                self._schema.Report.table(dataType='Summary', startTime=0, endTime=end_time),
            ))

        query = dsl_gql(DSLQuery(query_report))
        result = await self._session.execute(query)
        self._cache.set('gear_' + report_id, result)

        return result

    @tenacity.retry(wait=tenacity.wait_exponential(), stop=tenacity.stop_after_delay(120))
    async def get_bombs(self, report_id: str) -> Dict[str, Any]:
        """
        Gets data about bombs and other similar consumables.

        :param report_id: :class:`str` WarcraftLogs report ID.
        :return: GraphQL request result. Should be a JSON based dictionary object.
        """
        result = await self.get_report_times(report_id)
        cached_report = self.get_cache('bombs_' + report_id, result['reportData']['report']['endTime'])
        if cached_report:
            return cached_report

        end_time = result['reportData']['report']['endTime'] - result['reportData']['report']['startTime']
        bomb_spells = ','.join(utils.engineer.BOMB_SPELLS)
        other_spells = ','.join(utils.engineer.OTHER_SPELLS)

        query_report = self._schema.Query.reportData

        query_report.select(
            self._schema.ReportData.report(code=report_id).select(
                self._schema.Report.endTime,
                engineers=self._schema.Report.table(
                    dataType='Casts',
                    startTime=0,
                    endTime=end_time,
                    abilityID=utils.engineer.GLOVES_ENCHANT),
                bombs=self._schema.Report.table(
                    dataType='DamageTaken',
                    startTime=0,
                    endTime=end_time,
                    hostilityType='Enemies',
                    viewBy='Ability',
                    filterExpression=f'ability.ID in ({bomb_spells})'),
                others=self._schema.Report.table(
                    dataType='DamageTaken',
                    startTime=0,
                    endTime=end_time,
                    hostilityType='Enemies',
                    viewBy='Ability',
                    filterExpression=f'ability.ID in ({other_spells})'),
            ))

        query = dsl_gql(DSLQuery(query_report))
        result = await self._session.execute(query)
        self._cache.set('bombs_' + report_id, result)

        return result

    @tenacity.retry(wait=tenacity.wait_exponential(), stop=tenacity.stop_after_delay(120))
    async def get_events_combatantinfo(self, report_id: str) -> Dict[str, Any]:
        """
        Gets CombatantInfo events from WarcraftLog.

        :param report_id: :class:`str` WarcraftLogs report ID.
        :return: GraphQL request result. Should be a JSON based dictionary object.
        """

        result = await self.get_report_times(report_id)
        cached_report = self.get_cache('eci_' + report_id, result['reportData']['report']['endTime'])
        if cached_report:
            return cached_report

        end_time = result['reportData']['report']['endTime'] - result['reportData']['report']['startTime']

        query_report = self._schema.Query.reportData

        query_report.select(
            self._schema.ReportData.report(code=report_id).select(
                self._schema.Report.startTime,
                self._schema.Report.endTime,
                self._schema.Report.events(dataType='CombatantInfo', startTime=0, endTime=end_time).select(
                    self._schema.ReportEventPaginator.data),
            ))

        query = dsl_gql(DSLQuery(query_report))
        result = await self._session.execute(query)
        self._cache.set('eci_' + report_id, result)

        return result

    def get_cache(self, report_key: str, end_time: int) -> Optional[Dict]:
        cached_report = self._cache.get(report_key)

        if cached_report is None:
            return None

        if 'endTime' not in cached_report['reportData']['report']:
            return None

        if cached_report['reportData']['report']['endTime'] != end_time:
            return None

        return cached_report

    async def get_report_times(self, report_key: str) -> Optional[Dict]:
        query_report = self._schema.Query.reportData

        query_report.select(
            self._schema.ReportData.report(code=report_key).select(
                self._schema.Report.startTime,
                self._schema.Report.endTime,
                self._schema.Report.zone.select(self._schema.Zone.name),
            ))
        query = dsl_gql(DSLQuery(query_report))
        result = await self._session.execute(query)

        if result['reportData']['report']['zone']['name'] is None:
            raise Exception('Zone name not found')

        return result
