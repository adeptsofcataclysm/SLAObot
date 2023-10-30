from typing import Any, Optional

import discord
from discord import Embed

from slaobot import SlaoBot


class RaidViewButton(discord.ui.Button['RaidView']):
    def __init__(self, cog_name: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.cog_name = cog_name

    async def callback(self, interaction: discord.Interaction[SlaoBot]) -> None:
        report_id = self.view.validate_interaction(interaction)
        if report_id is None:
            await self.view.reply_with_error(interaction)
            return

        cog = interaction.client.get_cog(self.cog_name)
        if not cog:
            return

        await interaction.response.defer()

        embed = await cog.process_interaction(interaction)
        embeds = interaction.message.embeds

        if self.cog_name == 'raidreport':
            await interaction.edit_original_response(embed=embed)
        else:
            # Remove secondary embed if exists
            for item in embeds:
                if item.title == cog.embed_title:
                    embeds.remove(item)
                    await interaction.message.edit(embeds=embeds)
                    return

        # Add secondary embed if not exists
        embeds.append(embed)
        await interaction.edit_original_response(embeds=embeds)


class RaidView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        _button_init = [
            RaidViewButton(
                cog_name='raidreport',
                label='Refresh',
                custom_id='raid_view:refresh',
                style=discord.ButtonStyle.gray,
                emoji='🔄',
            ),
            RaidViewButton(
                cog_name='potions',
                label='Potions',
                custom_id='raid_view:potions',
                style=discord.ButtonStyle.gray,
                emoji='🧪',
            ),
            RaidViewButton(
                cog_name='gear',
                label='Gear',
                custom_id='raid_view:gear',
                style=discord.ButtonStyle.gray,
                emoji='🛂',
            ),
            RaidViewButton(
                cog_name='bomberman',
                label='Bombs',
                custom_id='raid_view:bombs',
                style=discord.ButtonStyle.gray,
                emoji='💣',
            ),
        ]
        for button in _button_init:
            self.add_item(button)

    @staticmethod
    def validate_interaction(interaction: discord.Interaction) -> Optional[str]:
        if interaction.message is None:
            return None

        # There should be an embed. Either waiting or report
        embed: Embed = interaction.message.embeds[0]
        if not embed:
            return None

        # Embed should have URL. I hope it is a WCL URL with report ID
        report_id = embed.url.split('/')[-1]
        if not report_id:
            return None

        return report_id

    @staticmethod
    async def reply_with_error(interaction: discord.Interaction) -> None:
        # noinspection PyUnresolvedReferences
        await interaction.response.send_message(
            'Embed or URL is missing. Something went wrong. Better call Doc!',
            ephemeral=True,
        )