# Part of the code Copyright 2020-2023 Lantis
# https://github.com/lantisnt/DKPBot
import sqlite3
from datetime import datetime
from sqlite3 import Connection, Cursor
from typing import Any, Dict, Optional

import discord
import pytz
from utils.constants import EXEC_VALUES


def make_time(timestamp: int, tz_name: str = None) -> str:
    digits = num_digits(timestamp)
    if digits > 10:
        timestamp = float(timestamp) / 1000

    fmt = '%Y-%m-%d %H:%M'
    if not tz_name:
        fmt = '%Y-%m-%d %H:%M (%z)'
        tz_name = 'Europe/Paris'

    local_time = datetime.fromtimestamp(timestamp, tz=pytz.timezone(tz_name))
    return local_time.strftime(fmt)


def num_digits(number: int) -> int:
    assert number > 0
    i = int(0.30102999566398114 * (number.bit_length() - 1)) + 1
    return (10 ** i <= number) + i


def make_execution(percent: int) -> str:
    index = int((percent - 1) / 25)
    return EXEC_VALUES[index]


def bold(string_like: Any) -> str:
    return f'**{string_like}**'


def build_error_embed(text: str) -> Dict[str, Any]:
    result = {
        'title': 'Critical Error',
        'description': text,
        'color': 14368774,
        'thumbnail_url': 'https://www.wowhcb.ru/slaobot/dkpbot-alert-error.png',
    }
    return result


def build_success_embed(text: str) -> Dict[str, Any]:
    result = {
        'title': 'Success',
        'description': text,
        'color': 2601546,
        'thumbnail_url': 'https://www.wowhcb.ru/slaobot/dkpbot-alert-success.png',
    }
    return result


def normalize_user(author):
    __SPLIT_DELIMITERS = ['#', '/', '\\', '|', ':', ';', '-', '(', ')', '[', ']']
    if isinstance(author, discord.Member):
        if author.nick:
            normalized = author.nick
        else:
            normalized = author
    else:
        normalized = author

    normalized = '{0}'.format(normalized)
    for delimiter in __SPLIT_DELIMITERS:
        normalized = normalized.split(delimiter)[0].strip()

    return normalized


def build_wowhead_item_link(item_name: str, item_id: int) -> str:
    return '[{1}](https://{0}/item={2})'.format('wowhead.com/cata/ru', item_name, item_id)


def build_loot_entries(entries: list, tz_name: str, show_target: bool = False) -> str:
    result = ''
    for entry in entries:
        _, target, _, _, _, _, gpb, gpa, item_id, item_name, timestamp, _, _ = entry
        gpb = gpb if gpb else 0
        gpa = gpa if gpa else 0
        if show_target:
            target = target if target else 'На шарды!'
            result += build_loot_entry(timestamp, gpa - gpb, item_name, item_id, tz_name, target)
        else:
            result += build_loot_entry(timestamp, gpa - gpb, item_name, item_id, tz_name)

    return result


def build_loot_entry(timestamp: int, gp: int, item_name: str, item_id: int, tz_name, target: Optional[str] = '') -> str:
    if not item_id:
        return '- No data available -'

    row = ''
    row += '`{0:16}` - '.format(make_time(timestamp, tz_name))
    row += '`{0:.0f} GP`'.format(gp)
    row += ' - ' + build_wowhead_item_link(item_name, item_id)
    if target:
        row += ' - '
        row += '{0}'.format(target)
    row += '\n'
    return row


def build_point_entries(entries: list, tz_name: str, show_target: bool = False) -> str:
    result = ''
    for entry in entries:
        _, target, source, descr, epb, epa, gpb, gpa, _, _, timestamp, _, _ = entry
        gpb = gpb if gpb else 0
        gpa = gpa if gpa else 0
        epb = epb if epb else 0
        epa = epa if epa else 0
        if show_target:
            result += build_point_entry(timestamp, epa - epb, gpa - gpb, descr, source, tz_name, target)
        else:
            result += build_point_entry(timestamp, epa - epb, gpa - gpb, descr, source, tz_name)

    return result


def build_point_entry(timestamp: int, ep: int, gp: int, descr: str, source: str, tz_name: str,
                      target: Optional[str] = '') -> str:
    if not source:
        return '- No data available -'

    row = ''
    row += '`{0:16}` - '.format(make_time(timestamp, tz_name))
    row += '`{0: >5.0f} EP {1: >3.0f} GP`'.format(ep, gp)
    row += ' - {0} _by {1}_'.format(descr, source)
    if target:
        row += ' - '
    row += '{0}'.format(target)
    row += '\n'
    return row


def build_epgp_footer(guild_id: str) -> str:
    db_name = f'./data/{guild_id}.db'
    db: Connection = sqlite3.connect(db_name)
    cursor: Cursor = db.cursor()

    cursor.execute('''SELECT * FROM History ORDER BY TIMESTAMP DESC''')
    _, user, timestamp = cursor.fetchone()
    cursor.close()
    db.close()
    return 'Последнее обновление - {0} | {1}'.format(user, '{0:16}'.format(make_time(timestamp)))


def build_epgp_list(entries: list) -> str:
    result = ''
    for entry in entries:
        player, ep, gp, pr = entry
        result += '`{0: >6.0f} EP` `{1: >4.0f} GP` `{2: >5.2f} PR`'.format(ep, gp, pr)
        result += '- {0}'.format(player)
        result += '\n'

    return result
