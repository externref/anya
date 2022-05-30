from __future__ import annotations

import hikari
import lightbulb, datetime
from core.bot import Bot


class Plugin(lightbulb.Plugin):
    def __init__(self) -> None:
        super().__init__(name="Shoob", description="Shoob Bot related commands")
        self.bot: Bot


plugin = Plugin()


@plugin.command
@lightbulb.command(
    name="recent", description="Recent card spawns in this server", aliases=["r"]
)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def recents(context: lightbulb.PrefixContext | lightbulb.SlashContext) -> None:
    spawns = await plugin.bot.cards_db.recent_guild_claims(context.guild_id)
    embed = hikari.Embed(color=plugin.bot.colors.peach_yellow).set_author(
        name=f"Last 5 claims in {context.get_guild().name}",
        icon=context.get_guild().icon_url,
    )
    embed.add_field(
        name="CARD",
        value="\n".join(
            [
                f"{_id}. `T{spawn.tier}` `{spawn.name}`{f'#`{spawn.v}`' if spawn.v else '' }"
                for _id, spawn in enumerate(spawns, start=1)
            ]
        ),
        inline=True,
    )
    embed.add_field(
        name="USER",
        value="\n".join(
            [
                (f"<@{spawn.claimer_id}>" if spawn.claimer_id else "`   ~   `")
                for spawn in spawns
            ]
        ),
        inline=True,
    )
    embed.add_field(
        name="SPAWNED",
        value="\n".join(
            [f"<t:{spawn.spawn_ts.timestamp().__int__()}:R>" for spawn in spawns]
        ),
        inline=True,
    )
    await context.respond(embed=embed)


def load(bot: Bot) -> None:
    bot.add_plugin(plugin)


def unload(bot: Bot) -> None:
    bot.remove_plugin(plugin)
