import asyncio
import concurrent.futures
import logging
import sqlite3
import time
from sqlite3 import Connection, Cursor

import discord
from discord import Embed, Message
from discord.ext import commands
from utils.config import guild_config
from utils.format import build_error_embed, build_success_embed, normalize_user
from utils.response import Response, ResponseStatus
from utils.savedvariables_parser import SavedVariablesParser

from slaobot import SlaoBot


class Clm(commands.Cog):
    __MAX_ATTACHMENT_BYTES = 25 * 1024 * 1024  # 25MB

    def __init__(self, bot: SlaoBot):
        """Cog to handle Classic Loot Manager data."""
        self.bot: SlaoBot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        # Do not listen DM channels
        if isinstance(message.channel, discord.DMChannel):
            return

        guild_id = str(message.guild.id)
        if not self._check_settings(guild_id):
            return

        if message.channel.id != guild_config[guild_id].getint('clm_upload_channel'):
            return

        # Process only message with attachments
        if len(message.attachments) == 0:
            return

        response = await self._process_attachment(message, guild_id)

        # Provide response
        await self.send_response(message.channel, response.data)

    async def send_response(self, channel, responses) -> None:
        if not responses:
            return

        if not isinstance(responses, list):
            response_list = [responses]
        else:
            response_list = responses

        for response in response_list:
            # Respond with message
            if isinstance(response, str):
                await channel.send(response)
            # Respond with embed
            elif isinstance(response, dict):
                await channel.send(embed=Embed.from_dict(response))

    def _check_settings(self, guild_id: str) -> bool:
        if not guild_config.has_section(guild_id):
            logging.error(f'Guild config not found for guild id {guild_id}')
            return False

        if not guild_config[guild_id].getboolean('clm_enabled'):
            return False

        if not guild_config[guild_id].getint('clm_upload_channel'):
            return False

        if not guild_config[guild_id].get('clm_server_side'):
            return False

        self._check_db(guild_id)

        return True

    def _check_db(self, guild_id: str) -> None:
        db_name = f'./data/{guild_id}.db'
        connection: Connection = sqlite3.connect(db_name)
        cursor: Cursor = connection.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS History (
            id INTEGER PRIMARY KEY,
            user TEXT NOT NULL,
            timestamp INTEGER NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Profile (
            id INTEGER PRIMARY KEY,
            user_guid TEXT NOT NULL,
            class TEXT,
            name TEXT
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Loot (
            id INTEGER PRIMARY KEY,
            user_guid TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            gp_value INTEGER NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS PointsHistory (
            id INTEGER PRIMARY KEY,
            user_guid TEXT NOT NULL,
            points_value INTEGER NOT NULL,
            timestamp INTEGER NOT NULL,
            reason INTEGER NOT NULL
        )
        ''')

        connection.commit()
        cursor.close()
        connection.close()

    async def _process_attachment(self, message: Message, guild_id: str) -> Response:
        for attachment in message.attachments:

            # Process only specific file name
            if attachment.filename != 'ClassicLootManager.lua':
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
                    message.author,
                    guild_id,
                )

        return response

    def _process_sv(self, data: str, author, guild_id: str) -> Response:
        addon_data = self._check_upload(data)
        if addon_data is None:
            return Response(ResponseStatus.ERROR,
                            build_error_embed
                            ('Error Parsing .lua file. Check if you have provided proper savedvariable file.'))

        # Get wowdkpbot data
        clm_data = self._get_clm_data(addon_data, guild_id)
        if clm_data is None:
            return Response(ResponseStatus.ERROR,
                            build_error_embed
                            ('Error getting CLM data. Check if you have provided proper savedvariable file.'))

        # Verify data
        if not self._check_clm_data(clm_data, guild_id):
            return Response(ResponseStatus.ERROR,
                            build_error_embed
                            ('Error verifying CLM data. Check if you have provided proper savedvariable file.'))

        db_name = f'./data/{guild_id}.db'
        self.connection: Connection = sqlite3.connect(db_name)
        self.cursor: Cursor = self.connection.cursor()

        # Process profile data
        profiles_data = clm_data.get('profiles')
        self.cursor.execute('''DELETE FROM Profile''')
        for player_guid, profile in profiles_data.items():
            self._parse_profile(player_guid, profile)

        # Process roster loot and points history
        roster_key = guild_config[guild_id].get('clm_roster_name')
        roster_data = clm_data.get('rosters').get(roster_key)

        # CLM provides full data each time. No need to keep previous imports.
        self.cursor.execute('''DELETE FROM Loot''')
        self.cursor.execute('''DELETE FROM PointsHistory''')
        for player_guid, player_data in roster_data.items():
            self._parse_loot(player_guid, player_data)
            self._parse_points_history(player_guid, player_data)

        # Update history
        self.cursor.execute('''INSERT INTO History (user, timestamp) VALUES (?,?)''',
                            (normalize_user(author), int(time.time())))

        self.connection.commit()
        self.cursor.close()
        self.connection.close()

        return Response(ResponseStatus.SUCCESS, build_success_embed('CLM database updated successfully.'))

    def _parse_profile(self, player_guid: str, data) -> None:
        if not player_guid or not data or not isinstance(data, dict):
            return

        # Get player name from Player-Server
        name = data.get('name').split('-')[0]
        if len(name) == 0:
            return

        self.cursor.execute(
            '''INSERT INTO Profile (user_guid, class, name) VALUES (?, ?, ?)''',
            (player_guid, data.get('class'), name),
        )

    def _parse_loot(self, player_guid: str, data) -> None:
        if not player_guid or not data or not isinstance(data, dict):
            return

        loot_list = data.get('loot')
        if not loot_list or not isinstance(loot_list, list):
            return

        for loot_entry in loot_list:
            if not isinstance(loot_entry, dict):
                continue

            item_id = loot_entry.get('id')
            item_name = loot_entry.get('name')
            timestamp = loot_entry.get('time')
            gp_value = loot_entry.get('value')

            if item_id is None or item_name is None or timestamp is None or gp_value is None:
                continue

            self.cursor.execute(
                '''INSERT INTO Loot (user_guid, item_id, item_name, timestamp, gp_value)
                   VALUES (?, ?, ?, ?, ?)''',
                (player_guid, item_id, item_name, timestamp, gp_value),
            )

    def _parse_points_history(self, player_guid: str, data) -> None:
        if not player_guid or not data or not isinstance(data, dict):
            return

        history_list = data.get('history')
        if not history_list or not isinstance(history_list, list):
            return

        for history_entry in history_list:
            if not isinstance(history_entry, dict):
                continue

            points_value = history_entry.get('value')
            timestamp = history_entry.get('time')
            reason = history_entry.get('reason')

            if points_value is None or timestamp is None or reason is None:
                continue

            self.cursor.execute(
                '''INSERT INTO PointsHistory (user_guid, points_value, timestamp, reason)
                   VALUES (?, ?, ?, ?)''',
                (player_guid, points_value, timestamp, reason),
            )

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

        addon_data = saved_variable.get('CLM2_DB')
        if addon_data is None or not addon_data or not isinstance(addon_data, dict):
            return None

        return addon_data

    def _get_clm_data(self, data: dict, guild_id: str):
        guild_key = guild_config[guild_id].get('clm_server_side')

        # Check if we have guild key in CLM data
        clm_guild_key = None
        for clm_guild in data.keys():
            if clm_guild.lower() == guild_key.lower():
                clm_guild_key = clm_guild
                break

        if clm_guild_key is None:
            self.bot.logger.debug(f'Guild key not found in CLM data for guild {guild_id}')
            return None

        guild_data = data.get(clm_guild_key)
        if guild_data is None:
            self.bot.logger.debug(f'Guild data not found in CLM data for guild {guild_id}')
            return None

        integration_data = guild_data.get('integration')
        if integration_data is None:
            self.bot.logger.debug(f'Integration data not found in CLM data for guild {guild_id}')
            return None

        bot_data = integration_data.get('wowdkpbot')
        if bot_data is None:
            self.bot.logger.debug(f'Wowdkpbot data not found in CLM data for guild {guild_id}')
            return None

        return bot_data

    def _check_clm_data(self, data: dict, guild_id: str) -> bool:
        # Verify rosters data
        rosters_data = data.get('rosters')
        if rosters_data is None or not rosters_data or not isinstance(rosters_data, dict):
            self.bot.logger.debug('Rosters data not found in CLM data')
            return False

        roster_key = guild_config[guild_id].get('clm_roster_name')
        roster_data = rosters_data.get(roster_key)
        if roster_data is None:
            self.bot.logger.debug(f'Roster data not found in CLM data for guild {guild_id}')
            return False

        # Validate profile data
        profiles_data = data.get('profiles')
        if profiles_data is None or not profiles_data or not isinstance(profiles_data, dict):
            self.bot.logger.debug('Profiles data not found in CLM data')
            return False

        return True


async def setup(bot):
    await bot.add_cog(Clm(bot))
