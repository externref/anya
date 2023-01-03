from __future__ import annotations

import typing

import hikari
import lightbulb
import toolbox

from core.utils import Hook, Plugin

if typing.TYPE_CHECKING:
    from core.bot import Anya

plugin = Plugin("greetings", "Greet your users!", 3)


@plugin.command
@lightbulb.command("greetings", "Add welcome/leave configs.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def greetings(_):
    ...


@lightbulb.Check
async def ensure_existence(context: lightbulb.Context) -> bool:
    await plugin.bot.db.pool.execute(  # type: ignore
        """
        INSERT INTO greetings
        VALUES ( $1 )
        ON CONFLICT DO NOTHING;
        """,
        context.guild_id,
    )
    return True


@greetings.child
@lightbulb.option(
    "channel", "Channel for messages.", type=hikari.GuildChannel, channel_types=[hikari.ChannelType.GUILD_TEXT]
)
@lightbulb.option("category", "Greeting category to set channel for.", choices=["welcome", "leave"])
@lightbulb.add_checks(ensure_existence | lightbulb.checks.has_guild_permissions(hikari.Permissions.MANAGE_CHANNELS))
@lightbulb.command("channel", "Channel for welcome/leave messages.", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def channel(context: lightbulb.SlashContext, channel: hikari.InteractionChannel, category: str) -> None:
    await context.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    member = (bot := plugin.bot).cache.get_member(
        context.guild_id or 0, bot.get_me()
    ) or await context.bot.rest.fetch_my_member(context.guild_id or 0)
    guild = context.get_guild() or await plugin.bot.rest.fetch_guild(context.guild_id or 0)
    _channel: hikari.PermissibleGuildChannel = guild.get_channel(channel.id) or await plugin.bot.rest.fetch_channel(channel.id)  # type: ignore
    perms = toolbox.calculate_permissions(member=member, channel=_channel)
    if not (perms & hikari.Permissions.SEND_MESSAGES and perms & hikari.Permissions.EMBED_LINKS):
        await context.interaction.edit_initial_response(
            embed=plugin.bot.fail_embed("Bot is missing required permissions (send message, embed links).")
        )
        return
    await plugin.bot.db.pool.execute(f"UPDATE greetings SET {category}_channel_id = $1 WHERE guild_id = $2", channel.id, context.guild_id)  # type: ignore

    await context.interaction.edit_initial_response(
        embed=plugin.bot.success_embed(f"Set {category} channel to {channel.mention} ({channel.name})")
    )


@Hook.create("greetings:loader")
def load(bot: Anya) -> None:
    bot.add_plugin(plugin)
    if bot.hooks.get("greetings:loader") is None:
        bot.hooks["greetings:loader"] = load
