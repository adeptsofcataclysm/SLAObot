import time

import discord
from discord import Colour, Embed, Member, app_commands
from discord.ext import commands
from discord.ext.commands import Context
from utils.config import settings

from slaobot import SlaoBot


class SignUpRequest(discord.ui.View):
    """View that will give starting role to a newcomer"""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Принять', style=discord.ButtonStyle.green, custom_id='sur:accept')
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.message is None:
            return None

        # noinspection PyUnresolvedReferences
        await interaction.response.defer()

        # There should be an embed with questionnaire answers
        embed: Embed = interaction.message.embeds[0]
        if not embed:
            return None

        try:
            mention = embed.fields[5].value
            mention = mention.replace('<', '')
            mention = mention.replace('>', '')
            mention = mention.replace('@', '')
            mention = mention.replace('!', '')

            candidate = interaction.guild.get_member(int(mention))
        except discord.NotFound:
            await interaction.followup.send('Не нашел пользователя.', ephemeral=True)
            return None

        role = discord.utils.get(interaction.guild.roles, name='Служитель')
        try:
            await candidate.add_roles(role)
        except discord.Forbidden:
            await interaction.followup.send('Нет прав.', ephemeral=True)
            return None

        # Role set. Let's update embed and stop the view
        embed.set_footer(text=f'{interaction.user} сделал Служителем | {time.asctime(time.localtime(time.time()))} ')
        await interaction.message.edit(embed=embed, view=None)
        self.stop()


class SignUpModal(discord.ui.Modal, title='Информация о себе'):
    """Modal dialog window with basic questions about newcomer."""

    name = discord.ui.TextInput(
        label='Твой имя',
        placeholder='Как тебя зовут',
        max_length=100,
        min_length=2,
    )

    character = discord.ui.TextInput(
        label='Имя персонажа',
        placeholder='Имя основного персонажа',
        max_length=100,
        min_length=2,
    )

    class_spec = discord.ui.TextInput(
        label='Класс и специализация',
        placeholder='Класс и основная специализация',
        max_length=100,
        min_length=2,
    )

    trade_skill = discord.ui.TextInput(
        label='Профессии',
        placeholder='Профессии и специализация в профессии, если есть',
        style=discord.TextStyle.long,
        required=False,
        max_length=100,
        min_length=2,
    )

    twinks = discord.ui.TextInput(
        label='Твинки',
        placeholder='Имена твинков и их класс',
        style=discord.TextStyle.long,
        required=False,
        max_length=100,
        min_length=2,
    )

    async def on_submit(self, interaction: discord.Interaction):

        signup_channel = interaction.client.get_channel(settings.signup_channel_id)

        if signup_channel:
            signup_embed = Embed(title='Новая заявка',
                                 description='Больше Адептов!!',
                                 colour=Colour.light_gray())
            signup_embed.add_field(name='Имя', value=self.name.value)
            signup_embed.add_field(name='Персонаж', value=self.character.value)
            signup_embed.add_field(name='Класс', value=self.class_spec.value)
            signup_embed.add_field(name='Профы', value=self.trade_skill.value)
            signup_embed.add_field(name='Твинки', value=self.twinks.value)
            signup_embed.add_field(name='Пользователь', value=format(interaction.user.mention))
            if interaction.user.avatar:
                signup_embed.set_thumbnail(url=interaction.user.avatar.url)
            await signup_channel.send(embed=signup_embed, view=SignUpRequest())

        # noinspection PyUnresolvedReferences
        await interaction.response.send_message(
            f'Спасибо, {self.name.value}! Офицеры в скором времени выдадут права в Discord',
            ephemeral=True,
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        # noinspection PyUnresolvedReferences
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)


class SignUp(commands.Cog):
    """Cog to greet newcomers and give them some basic questionnaire.

    :param bot: Bot instance
    """

    def __init__(self, bot: SlaoBot):
        self.bot: SlaoBot = bot
        # Register the persistent view for listening here.
        self.bot.add_view(SignUpRequest())

    @commands.Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        if member.bot:
            return

        if not member.guild.get_channel(settings.signup_channel_id):
            return

        dm_channel = await member.create_dm()
        intro_message = (f'Привет, {format(member.mention)}! \r\n'
                         'Приветствуем тебя на Discord сервере гильдии <Адепты Катаклизма>! \r\n'
                         'Мы играем в Cataclysm Classic за Альянс на Пламегоре. \r\n'
                         'Если хочешь вступить к нам в гильдию, то напиши /signup в любом  \r\n'
                         'канале Discord сервера Адептов. \r\n'
                         'Удачного времяпрепровождения!')

        await dm_channel.send(content=intro_message)

    @commands.command(hidden=True)
    async def emit_join(self, ctx: Context) -> None:
        """Emit member_join event."""
        self.bot.dispatch('member_join', ctx.author)

    @app_commands.command(description='Немного о себе')
    async def signup(self, interaction: discord.Interaction) -> None:
        # noinspection PyUnresolvedReferences
        await interaction.response.send_modal(SignUpModal())


async def setup(bot):
    await bot.add_cog(SignUp(bot))
