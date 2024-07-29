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
import logging
import re

import six
from slpp import SLPP


class WowLuaParser(SLPP):
    def decode(self, text):
        if not text or not isinstance(text, six.string_types):
            return
        # Remove only wow saved variable comments
        reg = re.compile('-{2,}\s+\[\d*\].*$', re.M)
        text = reg.sub('', text)
        self.text = text
        self.at, self.ch, self.depth = 0, '', 0
        self.len = len(text)
        self.next_chr()
        result = self.value()
        return result


wlp = WowLuaParser()


class SavedVariablesParser:
    def parse_string(self, input_string):
        # split variables
        strings = input_string.split('}\r\n')
        if not isinstance(strings, list):
            logging.error('Something not ok with split')
            return None

        pattern = re.compile('^\s*([a-zA-Z0-9-_]*)\s*=\s*')
        saved_variables = {}
        for string in strings:
            if len(string) == 0:
                continue
            string += '}'
            out = pattern.match(string)
            saved_variables[out.group().replace(' = ', '').strip()] = (
                wlp.decode(pattern.sub('', string, 1))
            )
        return saved_variables

    def parse_file(self, filepath):
        with open(filepath) as file:
            return self.parse_string(file.read())
