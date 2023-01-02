from __future__ import annotations

import time
import typing

import hikari
import lightbulb
import miru

from core.consts import INVITE_URL, Chars, ImageURLs
from core.utils import Hook, Plugin

if typing.TYPE_CHECKING:
    from core.bot import Anya
plugin = Plugin("Meta", "General bot commands.", 1)


@plugin.command
@lightbulb.command("ping", "Check bot latencies.")
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(context: lightbulb.SlashContext) -> None:
    initial = time.perf_counter()
    await context.respond(
        embed=plugin.bot.meta_embed("Checking latencies ...").set_author(name=f"{Chars.PING_PONG} Ping!")
    )
    rest_latency = (time.perf_counter()) - initial
    latencies: dict[str, float] = {
        "Bot Latency": plugin.bot.heartbeat_latency * 1000,
        "REST Latency": rest_latency * 1000,
    }
    latency_str = "\n".join(map(lambda a: f"{a[0]}: `{a[1]:.2f}ms`", latencies.items()))
    await context.edit_last_response(
        embed=plugin.bot.meta_embed(latency_str).set_author(name=f"{Chars.PING_PONG} Pong!")
    )


@plugin.command
@lightbulb.option("admin", "Set to true to invite bot with admin perms.", type=bool, default=False)
@lightbulb.command("invite", "Add the bot to your servers!.", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def invite(context: lightbulb.SlashContext, admin: bool) -> None:
    view = miru.View().add_item(
        miru.Button(
            style=hikari.ButtonStyle.LINK,
            label="Invite me!",
            url=(invite_url := INVITE_URL.format(perms=8 if admin is True else 516020358208)),
        )
    )
    await context.respond(
        embed=plugin.bot.meta_embed(f"Here's an URL to add me to your servers!\n> {invite_url}")
        .set_author(name=f"{Chars.PING_PONG} Invite me!")
        .set_image(ImageURLs.BANNER),
        components=view.build(),
    )


@Hook.create("meta:loader")
def load(bot: Anya) -> None:
    bot.add_plugin(plugin)
    if bot.hooks.get("meta:loader") is None:
        bot.hooks["meta:loader"] = load
