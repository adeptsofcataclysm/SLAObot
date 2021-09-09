from datetime import datetime, timezone
from typing import Any, Dict, List

from constants import SPECS, ZONE_NAMES
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
    def make_spec(characters: List[Dict[str, Any]], show_trophy: bool = False) -> str:
        result = ''

        if show_trophy:
            characters.sort(key=lambda x: x.get('total'), reverse=True)

        for place, char in enumerate(characters):
            if len(result) > 980:
                return result

            key = char['class'] + '_' + char['spec']
            spec = SPECS.get(key, '\u200b')

            if place < 3 and show_trophy:
                result += f'🏆 {spec}{bold(char["name"])} '
            else:
                result += spec + char['name'] + '  '

        return result

    @staticmethod
    def make_fight_info(fight: Dict[str, Any]) -> str:
        duration = datetime.fromtimestamp(fight['duration'] / 1000.0, timezone.utc).strftime('%Hч %Mм %Sс')
        value = f'Длительность: {bold(duration)}\n'
        value += f"Исполнение: {bold(make_execution(fight['execution']['rankPercent']))}\n"
        value += f"Скорость: {bold(fight['speed']['rankPercent'])}%"
        return value

    @classmethod
    def make_report_title(cls, rs: Dict[str, Any]) -> str:
        report_zone_id = cls.get_report_zone_id(rs)

        return ZONE_NAMES.get(report_zone_id, ZONE_NAMES.get(0))
