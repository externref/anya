from __future__ import annotations

import hikari
import lightbulb
from core.bot import Bot


class Plugin(lightbulb.Plugin):
    def __init__(self) -> None:
        super().__init__(name="Config", description="Bot configuration for you server.")
        self.pos = 1
        self.bot: Bot


plugin = Plugin()


@plugin.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD))
@lightbulb.option(
    name="new_prefix",
    description="The new server prefix",
    modifier=lightbulb.OptionModifier.CONSUME_REST,
)
@lightbulb.command(name="prefix", description="Change server prefix.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def change_prefix(
    context: lightbulb.PrefixContext | lightbulb.SlashContext,
) -> None:
    """Change the prefix of your server to the one you want.

    **Allowed Arguments:**
    `new_prefix`: The new prefix for the server.

    **Example Usage:** `anya prefix !`
    `!` is your new prefix now!

    Note: Discord markdown characters like `, #, @, *, / are not allowed.
    """

    if len(context.options.new_prefix) > 10 or any(
        (
            char in context.options.new_prefix
            for char in (
                "`",
                "/",
                "@",
                "#",
                "*",
            )
        )
    ):  # avoiding prefixes longer than 10 characters or with discord markdown.
        return await context.respond(
            embed=hikari.Embed(
                color=plugin.bot.colors.dark_red,
                description=(
                    "This could be because your prefix,"
                    "- Is more than 10 characters in length"
                    "\n- Has `, /, @, #, * markdown in it."
                ),
            ).set_author(name="Unable to set prefix."),
            reply=True,
        )

    await plugin.bot.prefix_db.set_prefix(context.guild_id, context.options.new_prefix)
    await context.respond(
        embed=hikari.Embed(
            color=plugin.bot.colors.green,
            description=f"Changed server prefix to `{context.options.new_prefix}`",
        ),
        reply=True,
    )


def load(bot: Bot) -> None:
    bot.add_plugin(plugin)


def unload(bot: Bot) -> None:
    bot.remove_plugin(plugin)
