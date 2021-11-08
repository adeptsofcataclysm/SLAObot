from collections import defaultdict
from datetime import datetime, timezone
from operator import attrgetter
from typing import Any, Dict, List

from constants import SPECS, ZONE_NAMES, Role
from models import Raider
from utils import bold, make_execution, make_time


class Report:

    @staticmethod
    def get_report_zone_id(rs: Dict[str, Any]) -> int:
        return rs['reportData']['report']['zone']['id']

    @staticmethod
    def make_report_description(rs: Dict[str, Any]) -> str:
        report_start = make_time(rs['reportData']['report']['startTime'])
        report_end = make_time(rs['reportData']['report']['endTime'])
        return f'{bold("Начало:")} {report_start} \n {bold("Окончание:")} {report_end}'

    @staticmethod
    def make_spec(raiders: List[Raider], show_trophy: bool = False) -> str:
        result = ''

        if show_trophy:
            raiders = sorted(raiders, key=attrgetter('total'), reverse=True)

        for place, raider in enumerate(raiders):
            if len(result) > 980:
                return result

            key = raider.class_ + '_' + raider.spec
            spec = SPECS.get(key, '\u200b')

            if place < 3 and show_trophy:
                result += f'🏆 {spec}{bold(raider.name)} '
            else:
                result += spec + raider.name + '  '

        return result

    @staticmethod
    def make_fight_info(fight: Dict[str, Any]) -> str:
        duration = datetime.fromtimestamp(fight['duration'] / 1000.0, timezone.utc).strftime('%Hч %Mм %Sс')
        value = f'Длительность: {bold(duration)}\n'
        try:
            execution = make_execution(fight['execution']['rankPercent'])
        except TypeError:
            execution = fight['execution']['rankPercent']

        value += f'Исполнение: {bold(execution)}\n'
        value += f"Скорость: {bold(fight['speed']['rankPercent'])}%"
        return value

    @classmethod
    def get_raiders_by_role(cls, rs: Dict[str, Any]) -> Dict[Role, List[Raider]]:
        raiders_by_role = cls._get_raiders_by_roles(rs)

        for role, was_done in ((Role.DPS, 'damageDone'), (Role.HEALER, 'healingDone')):
            cls._add_raiders_totals(
                raiders_by_role[role],
                rs['reportData']['report']['table']['data'][was_done],
            )

        return raiders_by_role

    @classmethod
    def make_report_title(cls, rs: Dict[str, Any]) -> str:
        report_zone_id = cls.get_report_zone_id(rs)

        return ZONE_NAMES.get(report_zone_id, ZONE_NAMES.get(0))

    @staticmethod
    def get_pot_usage_sorted(entries: Dict) -> str:
        pots = {}
        for entry in entries:
            pots[entry['name']] = entry['total']

        pots = sorted(pots.items(), key=lambda item: item[1], reverse=True)

        result = ''
        for key, value in pots:
            if len(result) > 0:
                result += ', '
            result += f'{key}({value})'

        return result if len(result) > 0 else 'Вагонимся'

    @staticmethod
    def _add_raiders_totals(raiders: List[Raider], characters: List[Dict[str, Any]]) -> Dict[str, int]:
        result = {}
        for raider in raiders:
            for char in characters:
                if char.get('name') == raider.name:
                    raider.total = char.get('total', float('+inf'))
                    continue

        return result

    @staticmethod
    def _get_raiders_by_roles(rs: Dict[str, Any]) -> Dict[Role, List[Raider]]:
        raiders = rs['reportData']['report']['table']['data']['composition']
        result = defaultdict(list)

        for raider in raiders:
            for spec in raider['specs']:
                try:
                    role = Role(spec.get('role'))
                except ValueError:
                    continue

                result[role].append(Raider(
                    name=raider['name'],
                    class_=raider['type'],
                    spec=spec['spec'],
                ))

        return result
