# Copyright 2020-2023 Lantis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum


class ResponseStatus(Enum):
    SUCCESS = 0
    ERROR = 1
    DELEGATE = 2
    RELOAD = 3
    SHUTDOWN = 90
    IGNORE = 99


class Response:
    status = ResponseStatus.IGNORE
    # Response on SUCCESS
    # Error information on ERROR
    # Request type on REQUEST
    # None on IGNORE
    data = None
    direct_message = False

    def __init__(self, status=ResponseStatus.IGNORE, data=None, direct_message=False):
        self.status = status
        self.data = data
        self.direct_message = bool(direct_message)
