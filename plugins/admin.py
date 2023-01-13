from __future__ import annotations

import typing

import hikari
import lightbulb

from core.utils import Eval, Hook, Plugin, command

if typing.TYPE_CHECKING:
    from core.bot import Anya
plugin = Plugin("admin", "interal stuff", 0)


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@command("Eval code", description="Evals code", guilds=(1035202799446794280,), pass_options=True)
@lightbulb.implements(lightbulb.MessageCommand)
async def eval_command(ctx: lightbulb.MessageContext, target: hikari.Message) -> None:
    _eval = Eval()
    if (code := target.content or "").startswith("```py"):
        code = code.replace("```py\n", "").replace("\n```", "")
    print(code, target.content)
    data = await _eval.f_eval(code=code, renv={"bot": plugin.bot, "ctx": ctx})
    await ctx.respond(f"```\n{data}\n```")


@Hook.create("admin:loader")
def load(bot: Anya) -> None:
    bot.add_plugin(plugin)
    if bot.hooks.get("admin:loader") is None:
        bot.hooks["admin:loader"] = load
