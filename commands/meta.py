from __future__ import annotations

import time
import typing

import hikari

from core.utils import Hook
from kai import SlashCommand

if typing.TYPE_CHECKING:
    from core.bot import Anya


@SlashCommand.init("ping", "Bot's latency.")
async def ping(bot: Anya, inter: hikari.CommandInteraction) -> None:
    initial = time.perf_counter()
    await inter.create_initial_response(
        hikari.ResponseType.MESSAGE_CREATE, embed=hikari.Embed(description="Checking latencies ...")
    )
    rest_latency = (time.perf_counter()) - initial
    latencies: dict[str, float] = {"Bot Latency": bot.heartbeat_latency * 1000, "REST Latency": rest_latency * 1000}
    latency_str = "\n".join(map(lambda a: f"{a[0]}: {a[1]:.2f}", latencies.items()))
    await inter.edit_initial_response(embed=hikari.Embed(description="\n".join(("```yaml", latency_str, "```"))))


@Hook.create("meta")
def setup(bot: Anya) -> None:
    for command in SlashCommand.in_file("commands.meta"):
        command.load_to(bot)
