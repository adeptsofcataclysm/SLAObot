# Part of the code Copyright 2020-2023 Lantis
# https://github.com/lantisnt/DKPBot
from datetime import datetime, timezone
from typing import Any, Dict

import discord
from utils.constants import EXEC_VALUES


def make_time(timestamp: int) -> str:
    digits = num_digits(timestamp)
    if digits > 10:
        timestamp = float(timestamp) / 1000

    utc_time = datetime.fromtimestamp(timestamp, timezone.utc)
    local_time = utc_time.astimezone()
    return local_time.strftime('%Y-%m-%d %H:%M (%z)')


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


def build_loot_entries(entries: list) -> str:
    result = ''
    for entry in entries:
        _, player, _, _, _, _, gpb, gpa, item_id, item_name, timestamp, _, _ = entry
        result += build_loot_entry(timestamp, gpa - gpb, item_name, item_id)

    return result


def build_loot_entry(timestamp: int, gp: int, item_name: str, item_id: int) -> str:
    if not item_id:
        return '- No data available -'

    row = ''
    row += '`{0:16}` - '.format(make_time(timestamp))
    row += '`{0:.0f} GP`'.format(gp)
    row += ' - ' + build_wowhead_item_link(item_name, item_id)
    row += '\n'
    return row


def build_point_entries(entries: list) -> str:
    result = ''
    for entry in entries:
        _, _, source, descr, epb, epa, gpb, gpa, _, _, timestamp, _, _ = entry
        result += build_point_entry(timestamp, epa - epb, gpa - gpb, descr, source)

    return result


def build_point_entry(timestamp: int, ep: int, gp: int, descr: str, source: str) -> str:
    if not source:
        return '- No data available -'

    row = ''
    row += '`{0:16}` - '.format(make_time(timestamp))
    row += '`{0:.0f}EP {1:.0f}GP`'.format(ep, gp)
    row += ' - {0} _by {1}_'.format(descr, source)
    row += '\n'
    return row
