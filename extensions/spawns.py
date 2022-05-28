from __future__ import annotations
import random

import hikari
import lightbulb
from core.bot import Bot

import asyncio


class Plugin(lightbulb.Plugin):
    def __init__(self) -> None:
        super().__init__("Spawns")
        self.ignored = True
        self.bot: Bot


plugin = Plugin()


def is_spawn_card(embed: hikari.Embed) -> bool:
    """
    Checking if the spawned card is a Shoob spawn card.

    Paramaters
    ----------

        embed: :class:`hikari.Embed`
            The embed to proccess

    Returns
    -------

        :class:`bool`

    """
    claim_texts = [
        "To claim, react to this message",
        "To claim, use `claim [captcha code]`",
    ]
    if any(quote in embed.description for quote in claim_texts):
        return True
    return False


def check_tier(embed: hikari.Embed) -> int:
    """
    Check the tier of the card spawned.

    Paramaters
    ----------

        embed: :class:`hikari.Embed`
            The embed to proccess

    Returns
    -------

        :class:`int`

    """
    if embed.color.__int__() == 16777215:
        return 1
    elif embed.color.__int__() == 8060813:
        return 2
    elif embed.color.__int__() == 5808355:
        return 3
    elif embed.color.__int__() == 11360483:
        return 4
    elif embed.color.__int__() == 16314629:
        return 5
    elif embed.color.__int__() == 15344162:
        return 6


@plugin.listener(hikari.GuildMessageCreateEvent)
async def on_spawn(event: hikari.GuildMessageCreateEvent) -> None:
    if event.message.author.id != 673362753489993749:
        return
    if len(event.message.embeds) == 0:
        return
    embed = event.message.embeds[0]
    if not is_spawn_card(embed):
        return

    tier = check_tier(embed)
    role_id = await plugin.bot.role_pings.get_role(tier, event.guild_id)

    if not role_id:
        return
    role = plugin.bot.cache.get_role(role_id)
    if not role:
        return
    await asyncio.sleep(random.randint(50, 200) / 100)
    embed = hikari.Embed(
        color=plugin.bot.colors.purple,
        description=f"`Tier {tier}` just spawned.",
    )
    await event.get_channel().send(
        role.mention,
        embed=embed,
        role_mentions=True,
    )


def load(bot: Bot) -> None:
    bot.add_plugin(plugin)
