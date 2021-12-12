from datetime import datetime, timezone
from typing import Any

from constants import EXEC_VALUES


def make_time(timestamp: int) -> str:
    utc_time = datetime.fromtimestamp(float(timestamp) / 1000, timezone.utc)
    local_time = utc_time.astimezone()
    return local_time.strftime('%Y-%m-%d %H:%M (%Z)')


def make_execution(percent: int) -> str:
    index = int((percent - 1) / 25)
    return EXEC_VALUES[index]


def bold(string_like: Any) -> str:
    return f'**{string_like}**'
