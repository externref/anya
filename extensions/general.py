from __future__ import annotations

import datetime

import hikari
import lightbulb
from core.bot import Bot


class Plugin(lightbulb.Plugin):
    def __init__(self) -> None:
        super().__init__(name="General", description="Commands for general purpose.")
        self.bot: Bot
        self.pos = 3


plugin = Plugin()


@plugin.command
@lightbulb.command(
    name="ping", description="Latency of the bot in ms", aliases=["latency"]
)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def ping_cmd(context: lightbulb.PrefixContext | lightbulb.SlashContext) -> None:
    await context.respond(
        embed=hikari.Embed(
            color=plugin.bot.colors.rose_pink,
            description=f"{plugin.bot.cache.get_emoji(981301275482284042)} Pong! `{round(context.bot.heartbeat_latency*1000, 2)}ms`",
        )
    )


@plugin.command
@lightbulb.command(name="commands", description="A list of all bot commands.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def list_commands(
    context: lightbulb.PrefixContext | lightbulb.SlashContext,
) -> None:
    embed = (
        hikari.Embed(
            color=plugin.bot.colors.peach_yellow,
            description=(
                "This is a list of all Prefix commands. "
                "You can use `/` and navigate to bot's menu on discord to view its slash commands."
            ),
        )
        .set_author(name="COMMAND LIST", icon=plugin.bot.get_me().avatar_url)
        .set_thumbnail("https://cdn.discordapp.com/emojis/981311615821565973.webp")
        .set_footer(
            text=f"Requested by {context.author}", icon=context.author.avatar_url
        )
    )
    plugins = list(context.bot.plugins.values())
    plugins.sort(key=lambda p: p.pos)
    for plgn in plugins:
        if getattr(plgn, "ignored", None):
            continue
        embed.add_field(
            name=f"{plgn.name.upper()} COMMANDS",
            value=f"```yaml\n{', '.join({cmd.name for cmd in plgn.all_commands})}\n```",
        )
    buttons = plugin.bot.rest.build_action_row()
    buttons.add_button(hikari.ButtonStyle.LINK, plugin.bot.invite_url).set_label(
        "Invite"
    ).set_emoji(981281185630134282).add_to_container()
    buttons.add_button(
        hikari.ButtonStyle.LINK, "https://sarthhh.github.io/anya"
    ).set_label("Docs").set_emoji(981281950255964170).add_to_container()
    await context.respond(embed=embed, reply=True, component=buttons)


def load(bot: Bot) -> None:
    bot.add_plugin(plugin)


def unload(bot: Bot) -> None:
    bot.remove_plugin(plugin)