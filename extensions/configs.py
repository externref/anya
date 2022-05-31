from __future__ import annotations

import hikari
import lightbulb
from core.bot import Bot


class Plugin(lightbulb.Plugin):
    def __init__(self) -> None:
        super().__init__(name="Config", description="Bot configuration for you server.")
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
    """Command to set custom prefixes for servers."""

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


@plugin.command
@lightbulb.option(name="role", description="Role to ping on spawn", type=hikari.Role)
@lightbulb.option(
    name="tier",
    description="Tier to set role for",
    choices=["Tier1", "Tier2", "Tier3", "Tier4", "Tier5", "Tier6"],
)
@lightbulb.command(name="set_role", description="Set role pings for Shoob card spawns")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def set_role(
    context: lightbulb.PrefixContext | lightbulb.SlashContext,
):
    """Setting role pings for Shoob card spawns"""
    tier = context.options.tier.lower()
    role: hikari.Role = context.options.role
    valid_tiers = ["tier1", "tier2", "tier3", "tier4", "tier5", "tier6"]
    if tier.lower() not in valid_tiers:
        return await context.respond(
            embed=hikari.Embed(
                color=plugin.bot.colors.dark_red,
                description=f"Tier must be one from: `{'`, `'.join(valid_tiers)}`",
            ),
            reply=True,
        )
    await plugin.bot.role_pings.set_role(
        context.guild_id, int(tier.lower().replace("tier", "")), context.options.role.id
    )
    await context.respond(
        embed=hikari.Embed(
            color=plugin.bot.colors.green,
            description=f"Set role pings for `{tier.upper()}` to `{role.name}` ({role.mention}) ",
        ),
        reply=True,
    )


def load(bot: Bot) -> None:
    bot.add_plugin(plugin)


def unload(bot: Bot) -> None:
    bot.remove_plugin(plugin)
