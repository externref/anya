from __future__ import annotations

import datetime

import hikari
import lightbulb
from core.bot import Bot


class Plugin(lightbulb.Plugin):
    def __init__(self) -> None:
        super().__init__(name="Shoob", description="Shoob Bot related commands")
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
                f"{_id}. `T{spawn.tier}` `{spawn.name}`{f'#`{spawn.v}`' if spawn.v else '' }"
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
    await context.respond(embed=embed)


def load(bot: Bot) -> None:
    bot.add_plugin(plugin)


def unload(bot: Bot) -> None:
    bot.remove_plugin(plugin)
