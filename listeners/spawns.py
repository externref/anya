from __future__ import annotations

import hikari
import lightbulb
from core.bot import Bot


class Plugin(lightbulb.Plugin):
    def __init__(self) -> None:
        super().__init__("Spawns")
        self.ignored = True
        self.bot: Bot
        self.spawn_cards: dict[int, hikari.Embed] = {}
        self.pos = -1


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
    plugin.spawn_cards[event.channel_id] = embed
    try:
        event_2: hikari.GuildMessageCreateEvent = await plugin.bot.wait_for(
            hikari.GuildMessageCreateEvent,
            predicate=lambda e: e.channel_id == event.channel_id
            and e.author_id == event.author_id
            and len(e.message.embeds) > 0
            and e.message.embeds[0].description.__contains__("got the"),
            timeout=60,
        )
        await plugin.bot.cards_db.insert_spawn_data(
            event.guild_id,
            event.message.created_at.timestamp().__int__(),
            embed.title,
            check_tier(embed),
            embed.url,
            int(
                event_2.message.embeds[0]
                .description.split("#:")[1]
                .replace(".", "")
                .replace("`", "")
            ),
            int(
                event_2.message.embeds[0]
                .description.split(">")[0]
                .replace("!", "")
                .replace("@", "")
                .replace("<", "")
            ),
        )
    except __import__("asyncio").TimeoutError:
        await plugin.bot.cards_db.insert_spawn_data(
            event.guild_id,
            event.message.created_at.timestamp().__int__(),
            embed.title,
            check_tier(embed),
            embed.url,
        )
    plugin.spawn_cards.pop(event.channel_id)


@plugin.listener(hikari.GuildMessageUpdateEvent)
async def on_despawn(event: hikari.GuildMessageUpdateEvent) -> None:
    if not plugin.spawn_cards.get(event.channel_id):
        return
    if event.old_message.author.id != 673362753489993749:
        return
    spawn = plugin.spawn_cards.get(event.channel_id)
    if not event.old_message.embeds[0] == spawn:
        return
    await plugin.bot.cards_db.insert_spawn_data(
        event.guild_id,
        event.message.created_at.timestamp().__int__(),
        spawn.title,
        check_tier(spawn),
        spawn.url,
    )
    plugin.spawn_cards.pop(event.channel_id)


@plugin.listener(hikari.GuildMessageDeleteEvent)
async def on_despawn_2(event: hikari.GuildMessageDeleteEvent) -> None:
    if not plugin.spawn_cards.get(event.channel_id):
        return
    if event.old_message.author.id != 673362753489993749:
        return
    spawn = plugin.spawn_cards.get(event.channel_id)
    if not event.old_message.embeds[0] == spawn:
        return
    await plugin.bot.cards_db.insert_spawn_data(
        event.guild_id,
        event.message.created_at.timestamp().__int__(),
        spawn.title,
        check_tier(spawn),
        spawn.url,
    )
    plugin.spawn_cards.pop(event.channel_id)


def load(bot: Bot) -> None:
    bot.add_plugin(plugin)
