from __future__ import annotations

import datetime

import hikari
import lightbulb
from core.bot import Bot


class Plugin(lightbulb.Plugin):
    def __init__(self) -> None:
        super().__init__(
            name="Shoob", description="Commands extending shoob bot functionality."
        )
        self.bot: Bot
        self.pos = 0


plugin = Plugin()


def get_embed(context: hikari.Member, spawns) -> hikari.Embed:
    embed = (
        hikari.Embed(color=plugin.bot.colors.peach_yellow)
        .set_author(
            name=f"Last 5 claims in {context.get_guild().name}",
            icon=context.get_guild().icon_url,
        )
        .set_footer(
            text=f"Requested by {context.author}", icon=context.author.avatar_url
        )
    )
    embed.add_field(
        name="CARD",
        value="\n".join(
            [
                f"{_id}. `T{spawn.tier}` {f'[`{spawn.name}`]({spawn.url})' if spawn.url else f'`{spawn.name}`'}{f' #`{spawn.v}`' if spawn.v else '' }"
                for _id, spawn in enumerate(spawns, start=1)
            ]
        )
        or "`  ~~~  `",
        inline=True,
    )
    embed.add_field(
        name="USER",
        value="\n".join(
            [
                (f"<@{spawn.claimer_id}>" if spawn.claimer_id else "`   ~   `")
                for spawn in spawns
            ]
        )
        or "`  ~~~  `",
        inline=True,
    )
    embed.add_field(
        name="SPAWNED",
        value="\n".join(
            [f"<t:{spawn.spawn_ts.timestamp().__int__()}:R>" for spawn in spawns]
        )
        or "`  ~~~  `",
        inline=True,
    )
    return embed


@plugin.command
@lightbulb.option(
    name="category",
    description="Type of recent spawns to view.",
    choices=[
        "claimed",
        "despawned",
        "TIER1",
        "TIER2",
        "TIER3",
        "TIER4",
        "TIER5",
        "TIER6",
    ],
    required=False,
)
@lightbulb.command(
    name="recent", description="Recent card spawns in this server", aliases=["r"]
)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def recents(context: lightbulb.PrefixContext | lightbulb.SlashContext) -> None:
    category = context.options.category.lower() if context.options.category else ""

    if category in ("despawned", "--d"):
        spawns = await plugin.bot.cards_db.recent_guild_despawns(context.guild_id)
    elif category in ("claimed", "--c"):
        spawns = await plugin.bot.cards_db.recent_guild_claims(context.guild_id)
    elif category in (
        "tier1",
        "t1",
        "tier2",
        "t2",
        "tier3",
        "t3",
        "tier4",
        "t4",
        "tier5",
        "t5",
        "tier6",
        "t6",
    ):
        spawns = await plugin.bot.cards_db.recent_tier_spawns(
            context.guild_id, int(category.strip("tier"))
        )
    else:
        spawns = await plugin.bot.cards_db.recent_guild_spawns(context.guild_id)
    embed = get_embed(context, spawns)
    await context.respond(embed=embed, reply=True)


@plugin.command
@lightbulb.command(
    name="stats", description="Get the server's stats based on bot's records."
)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def lb_command(context: lightbulb.PrefixContext | lightbulb.SlashContext) -> None:
    data = await plugin.bot.cards_db.get_all_spawns(context.guild_id)
    tier1 = [card for card in data if card.tier == 1]
    tier2 = [card for card in data if card.tier == 2]
    tier3 = [card for card in data if card.tier == 3]
    tier4 = [card for card in data if card.tier == 4]
    tier5 = [card for card in data if card.tier == 5]
    tier6 = [card for card in data if card.tier == 6]
    members = {card.claimer_id for card in data}

    def get_despawned_count(tier: list) -> int:
        return len([card for card in tier if card.claimer_id is None])

    def string_for_tier(tier: list, n: int) -> str:
        return f"**Tier {n}**: `{len(tier)}` Spawns, `{len(tier)-get_despawned_count(tier)}` Claims, `{get_despawned_count(tier)}` Despawns"

    embed = (
        hikari.Embed(color=plugin.bot.colors.purple)
        .set_author(
            name=f"Stats for {context.get_guild()}", icon=plugin.bot.get_me().avatar_url
        )
        .set_thumbnail(context.get_guild().icon_url)
        .set_footer(text="This data based on what messages the bot is able to read.")
    )
    embed.description = (
        f"Server: {context.get_guild().name}\n"
        f"Total claims: {len(data)}\n"
        f"Card Claimers: {len(members)}"
    )

    embed.add_field(
        name="CARD STATS",
        value="\n".join(
            [
                string_for_tier(tier, tier_n)
                if tier
                else f"**Tier {tier_n}**: `No spawns yet`"
                for tier_n, tier in enumerate(
                    [tier1, tier2, tier3, tier4, tier5, tier6], start=1
                )
            ]
        ),
    )

    await context.respond(embed=embed, reply=True)


def load(bot: Bot) -> None:
    bot.add_plugin(plugin)


def unload(bot: Bot) -> None:
    bot.remove_plugin(plugin)
