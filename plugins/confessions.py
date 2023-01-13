from __future__ import annotations

import typing

import hikari
import lightbulb
import toolbox

from components.views import ConfessionView
from core.errors import ConfessionConfigMissing
from core.utils import Hook, Plugin, command

if typing.TYPE_CHECKING:
    from core.bot import Anya


@lightbulb.Check
async def ensure_existence(context: lightbulb.Context) -> bool:
    await plugin.bot.db.pool.execute(  # type: ignore
        "INSERT INTO confession_configs VALUES ( $1 ) ON CONFLICT DO NOTHING", context.guild_id
    )
    _id: int = await plugin.bot.db.pool.fetchval(  # type: ignore
        "SELECT channel_id FROM confession_configs WHERE guild_id = $1", context.guild_id
    )
    if _id:
        return True
    raise ConfessionConfigMissing(f"No confession channel set up for {context.guild_id}")


plugin = Plugin("confessions", "Confession system.", 2)


@plugin.command
@command("confession", "-")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def base(_: lightbulb.SlashContext) -> None:
    ...


@base.child
@lightbulb.option("channel", "The channel to add.", hikari.GuildChannel, channel_types=[hikari.ChannelType.GUILD_TEXT])
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD))
@command("channel", "Set channel for confession messages.", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def channel(context: lightbulb.SlashContext, channel: hikari.InteractionChannel) -> None:
    member = plugin.bot.cache.get_member(
        context.guild_id or 1, plugin.bot.get_me()
    ) or await plugin.bot.rest.fetch_member(context.guild_id or 0, plugin.bot.get_me())
    _channel = plugin.bot.cache.get_guild_channel(channel.id) or await plugin.bot.rest.fetch_channel(channel.id)
    perms = toolbox.calculate_permissions(member=member, channel=_channel)  # type: ignore
    if not (perms & hikari.Permissions.SEND_MESSAGES and perms & hikari.Permissions.EMBED_LINKS):
        await context.respond(
            embed=plugin.bot.fail_embed("Bot is missing required permissions (send message, embed links).")
        )
        return
    await plugin.bot.db.pool.execute(  # type: ignore
        "UPDATE confession_configs SET channel_id = $1 WHERE guild_id = $2 ", channel.id, context.guild_id
    )
    await context.respond(plugin.bot.success_embed(f"Set confession channel to {channel.mention} (`{channel.name}`)"))


@base.child
@lightbulb.add_checks(ensure_existence)
@command("create", "Create a confession")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def confess(context: lightbulb.SlashContext) -> None:
    res = await context.respond(components=(view := ConfessionView()).build(), flags=hikari.MessageFlag.EPHEMERAL)
    await view.start(res)


@Hook.create("confessions:loader")
def load(bot: Anya) -> None:
    bot.add_plugin(plugin)
    load.add_to_bot(bot)
