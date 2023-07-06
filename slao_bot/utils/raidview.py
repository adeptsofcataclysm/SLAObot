import discord
from discord import Embed

from slaobot import SlaoBot


def _validate_interaction(interaction: discord.Interaction) -> bool:
    if interaction.message is None:
        return False

    report_embed: Embed = interaction.message.embeds[0]
    if not report_embed:
        return False

    return True


class RaidView(discord.ui.View):
    def __init__(self, bot: SlaoBot):
        super().__init__(timeout=None)
        self.bot: SlaoBot = bot

    @discord.ui.button(label='Refresh', style=discord.ButtonStyle.gray, custom_id='raid_view:refresh', emoji='🔄')
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not _validate_interaction(interaction):
            return

        if interaction.message.embeds[0].url:
            # Waiting embed
            report_id = interaction.message.embeds[0].url.split('/')[-1]
            author_icon = interaction.message.embeds[0].thumbnail.url
        else:
            # Rankings embed
            report_id = interaction.message.embeds[0].author.url.split('/')[-1]
            author_icon = interaction.message.embeds[0].author.icon_url

        if report_id:
            cog = self.bot.get_cog('RaidReport')
            if not cog:
                return

            ctx = await self.bot.get_context(interaction.message)
            await interaction.message.delete()
            await cog.process_report(ctx, report_id, author_icon)

    @discord.ui.button(label='Potions', style=discord.ButtonStyle.gray, custom_id='raid_view:potions', emoji='🧪')
    async def potions(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not _validate_interaction(interaction):
            return

        if interaction.message.embeds[0].url:
            # Waiting embed
            return

        report_id = interaction.message.embeds[0].author.url.split('/')[-1]
        if not report_id:
            return

        cog = self.bot.get_cog('Potions')
        if not cog:
            return

        await interaction.response.defer()

        # Remove potions embed if exists
        current_embeds = interaction.message.embeds
        for item in current_embeds:
            if item.title == 'Расходники':
                current_embeds.remove(item)
                await interaction.message.edit(embeds=current_embeds)
                return

        # Add potion embeds if not exists
        ctx = await self.bot.get_context(interaction.message)
        await cog.process_pots(ctx, report_id)

    @discord.ui.button(label='Gear', style=discord.ButtonStyle.gray, custom_id='raid_view:gear', emoji='🛂')
    async def gear(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not _validate_interaction(interaction):
            return

        if interaction.message.embeds[0].url:
            # Waiting embed
            return

        report_id = interaction.message.embeds[0].author.url.split('/')[-1]
        if not report_id:
            return

        cog = self.bot.get_cog('Gear')
        if not cog:
            return

        await interaction.response.defer()

        # Remove gear embed if exists
        current_embeds = interaction.message.embeds
        for item in current_embeds:
            if item.title == 'Камни и зачаровывание':
                current_embeds.remove(item)
                await interaction.message.edit(embeds=current_embeds)
                return

        # Add gear embeds if not exists
        ctx = await self.bot.get_context(interaction.message)
        await cog.process_gear(ctx, report_id)

    @discord.ui.button(label='Bombs', style=discord.ButtonStyle.gray, custom_id='raid_view:bombs', emoji='💣')
    async def bombs(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not _validate_interaction(interaction):
            return

        if interaction.message.embeds[0].url:
            # Waiting embed
            return

        report_id = interaction.message.embeds[0].author.url.split('/')[-1]
        if not report_id:
            return

        cog = self.bot.get_cog('Bomberman')
        if not cog:
            return

        await interaction.response.defer()

        # Remove gear embed if exists
        current_embeds = interaction.message.embeds
        for item in current_embeds:
            if item.title == 'Бомбим!':
                current_embeds.remove(item)
                await interaction.message.edit(embeds=current_embeds)
                return

        # Add gear embeds if not exists
        ctx = await self.bot.get_context(interaction.message)
        await cog.process_bombs(ctx, report_id)
