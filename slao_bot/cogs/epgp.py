# Part of the code Copyright 2020-2023 Lantis
# https://github.com/lantisnt/DKPBot

import asyncio
import concurrent.futures
import re
import sqlite3
import time
from sqlite3 import Connection, Cursor
from typing import Optional

import discord
from discord import Embed, Message, app_commands
from discord.ext import commands
from utils.format import (
    build_error_embed, build_loot_entries, build_point_entries,
    build_success_embed, make_time, normalize_user,
)
from utils.response import Response, ResponseStatus
from utils.savedvariables_parser import SavedVariablesParser

from slaobot import SlaoBot


class Epgp(commands.Cog):
    __MAX_ATTACHMENT_BYTES = 25 * 1024 * 1024  # 25MB
    __item_id_name_find = re.compile('^[^:]*:*(\d*).*\[([^\]]*)', re.I)

    def __init__(self, bot: SlaoBot):
        """Cog to handle EPGP."""
        self.bot: SlaoBot = bot
        self._check_db()

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        # Do not listen DM channels
        if isinstance(message.channel, discord.DMChannel):
            return

        # Process only message with attachments
        if len(message.attachments) == 0:
            return

        response = await self._process_attachment(message)

        # Provide response
        await self.send_response(message.channel, response.data)

    @app_commands.command(description='Показать EPGP персонажа')
    @app_commands.describe(target='Имя персонажа или all')
    async def epgp(self, interaction: discord.Interaction, target: Optional[str] = None) -> None:
        """Get epgp data. """
        # noinspection PyUnresolvedReferences
        await interaction.response.defer()

        if target is None:
            target = normalize_user(interaction.user)

        embed = await self.process_epgp(target)
        if embed is None:
            embed = Embed.from_dict(build_error_embed('Нет информации по персонажу {0}'.format(target)))

        await interaction.edit_original_response(embed=embed)

    async def process_epgp(self, target: str) -> Optional[discord.Embed]:
        connection: Connection = sqlite3.connect('./data/epgp.db')
        cursor: Cursor = connection.cursor()

        cursor.execute('''SELECT * FROM Standing WHERE player=?''', (target,))
        standing = cursor.fetchone()
        if standing is None:
            return None

        _, player, ep, gp = standing

        embed = Embed(title=player, description='', colour=10204605)
        embed.set_thumbnail(url='https://www.wowhcb.ru/slaobot/CEPGP.png')
        embed.add_field(name='Effort Points:', value='`{0:.0f} EP`'.format(ep), inline=True)
        embed.add_field(name='Gear Points:', value='`{0:.0f} GP`'.format(gp), inline=True)
        embed.add_field(name='Приоритет:', value='`{0:.2f} PR`'.format(ep / gp), inline=True)

        # Latest EP
        cursor.execute('''SELECT * FROM Traffic WHERE item_id IS NULL AND target=? ORDER BY TIMESTAMP DESC''',
                       (target,))
        latest_points = cursor.fetchmany(3)
        embed.add_field(name='Последние начисления',
                        value=build_point_entries(latest_points),
                        inline=False)

        # Latest loot
        cursor.execute('''SELECT * FROM Traffic WHERE item_id IS NOT NULL AND target=? ORDER BY TIMESTAMP DESC''',
                       (target,))
        loot_entries = cursor.fetchmany(3)
        embed.add_field(name='Последняя добыча',
                        value=build_loot_entries(loot_entries),
                        inline=False)

        # Footer
        cursor.execute('''SELECT * FROM History ORDER BY TIMESTAMP DESC''')
        _, user, timestamp = cursor.fetchone()
        embed.set_footer(text='Последнее обновление - {0} | {1}'.
                         format(user, '{0:16}'.format(make_time(timestamp))))
        return embed

    async def send_response(self, channel, responses) -> None:
        if not responses:
            return

        if not isinstance(responses, list):
            response_list = [responses]
        else:
            response_list = responses

        for response in response_list:
            if isinstance(response, str):
                # Respond with message
                await channel.send(response)
            elif isinstance(response, dict):
                # Respond with embed
                await channel.send(embed=Embed.from_dict(response))

    def _check_db(self):
        self.connection: Connection = sqlite3.connect('./data/epgp.db')
        self.cursor: Cursor = self.connection.cursor()
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Traffic (
            id INTEGER PRIMARY KEY,
            target TEXT,
            source TEXT NOT NULL,
            descr TEXT,
            epb INTEGER,
            epa INTEGER,
            gpb INTEGER,
            gpa INTEGER,
            item_id INTEGER,
            item_name TEXT,
            timestamp INTEGER NOT NULL,
            cepgp_id REAL,
            unit_guid TEXT
        )
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS History (
            id INTEGER PRIMARY KEY,
            user TEXT NOT NULL,
            timestamp INTEGER NOT NULL
        )
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Standing (
            id INTEGER PRIMARY KEY,
            player TEXT NOT NULL,
            ep INTEGER NOT NULL,
            gp INTEGER NOT NULL
        )
        ''')
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    async def _process_attachment(self, message: Message) -> Response:
        for attachment in message.attachments:

            # Process only specific file name
            if attachment.filename != 'CEPGP.lua':
                return Response(ResponseStatus.ERROR,
                                build_error_embed('Wrong file name. Please, provide proper file.'))

            # We have a limit for attachments
            if attachment.size >= self.__MAX_ATTACHMENT_BYTES:
                return Response(ResponseStatus.ERROR,
                                build_error_embed('File is too large. Please, shrink EPGP traffic'))

            # Process attachment
            attachment_bytes = await attachment.read()
            loop = asyncio.get_running_loop()

            with concurrent.futures.ThreadPoolExecutor() as pool:
                response = await loop.run_in_executor(
                    pool,
                    self._process_sv,
                    attachment_bytes.decode('utf-8', errors='replace'),
                    message.author)

        return response

    def _process_sv(self, data: str, author) -> Response:

        addon_data = self._check_upload(data)
        if addon_data is None:
            return Response(ResponseStatus.ERROR,
                            build_error_embed
                            ('Error Parsing .lua file. Check if you have provided proper savedvariable file.'))

        # Validate Traffic
        traffic_list = self._check_traffic(addon_data)
        if traffic_list is None:
            return Response(ResponseStatus.ERROR,
                            build_error_embed
                            ('Traffic data not found in .lua file. '
                             'Check if you have provided proper savedvariable file.'))

        # Validate Standing
        backup = self._check_standing(addon_data)
        if backup is None:
            return Response(ResponseStatus.ERROR,
                            build_error_embed
                            ('Standing data not found in .lua file. '
                             'Check if you have provided proper savedvariable file.'))

        self.connection: Connection = sqlite3.connect('./data/epgp.db')
        self.cursor: Cursor = self.connection.cursor()

        # Process Traffic
        for traffic in traffic_list:
            self._parse_traffic_entry(traffic)

        # Process Standing
        for player_slug, data in backup.items():
            self._parse_standing(player_slug, data)

        # Update history
        self.cursor.execute('''INSERT INTO History (user, timestamp) VALUES (?,?)''',
                            (normalize_user(author), int(time.time())))

        self.connection.commit()
        self.cursor.close()
        self.connection.close()

        return Response(ResponseStatus.SUCCESS, build_success_embed('EPGP database updated successfully.'))

    def _check_upload(self, data: str):
        """ Tries to parse uploaded file. """
        try:
            saved_variable = SavedVariablesParser().parse_string(data)
        except AttributeError:
            return None

        if saved_variable is None:
            return None

        if not isinstance(saved_variable, dict):
            return None

        addon_data = saved_variable.get('CEPGP')
        if addon_data is None or not addon_data or not isinstance(addon_data, dict):
            return None

        return addon_data

    def _check_traffic(self, data: dict):
        traffic_list = data.get('Traffic')
        if traffic_list is None or not traffic_list or not isinstance(traffic_list, list):
            return None

        return traffic_list

    def _check_standing(self, data: dict):
        backups_list = data.get('Backups')
        if backups_list is None or not backups_list or not isinstance(backups_list, dict):
            return None

        backup = backups_list.get('bot')
        if backup is None or not backup or not isinstance(backup, dict):
            return None

        if len(backup) == 0:
            return None

        return backup

    def _parse_traffic_entry(self, traffic_entry: list) -> None:

        # Unpack CEPGP Traffic entry
        (target, source, descr, epb, epa,
         gpb, gpa, item_link, timestamp,
         cepgp_id, unit_guid) = (traffic_entry
                                 or (None, None, None, None, None, None, None, None, None, None, None))

        if cepgp_id is None:
            return

        # Check entry for existence in DB
        self.cursor.execute('SELECT id FROM Traffic WHERE cepgp_id=?', (cepgp_id,))
        if not self.cursor.fetchone() is None:
            # Traffic entry already in DB
            return

        # Check for item entry
        item_id = item_name = None
        item_info = self._get_item_id_name(item_link)
        if (item_info and isinstance(item_info, list) and len(item_info) == 1 and item_info[0]
                and isinstance(item_info[0], tuple) and len(item_info[0]) == 2):
            # We have found 1 item entry in ItemLink
            item_id = item_info[0][0]
            item_name = item_info[0][1]

        self.cursor.execute('''
        INSERT INTO
        Traffic (target, source, descr, epb, epa, gpb, gpa, item_id, item_name, timestamp, cepgp_id, unit_guid)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (target, source, descr, epb, epa, gpb, gpa, item_id, item_name, timestamp, cepgp_id,
              unit_guid))

    def _parse_standing(self, player_slug, data):

        if not player_slug or not data:
            return

        # Get player name from Player-Server
        player = player_slug.split('-')[0]
        if len(player) == 0:
            return

        # Get EP and GP values
        if len(data) <= 0:
            return

        tmp = data.split(',')
        if len(tmp) != 2:
            return

        ep = float(tmp[0])
        gp = max(float(tmp[1]), 1)

        self.cursor.execute('''SELECT id FROM Standing WHERE player=?''', (player,))
        if not self.cursor.fetchone() is None:
            # Player entry already in DB
            self.cursor.execute('''UPDATE Standing SET ep=?, gp=? WHERE player=?''', (ep, gp, player))
        else:
            self.cursor.execute('''INSERT INTO Standing (player, ep, gp) VALUES (?, ?, ?)''',
                                (player, ep, gp))

    def _get_item_id_name(self, loot):
        # [0] -> id [1] -> name
        return list(filter(None, type(self).__item_id_name_find.findall(loot)))


async def setup(bot):
    await bot.add_cog(Epgp(bot))
