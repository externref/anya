# noqa: E501

from __future__ import annotations

import typing

import hikari
import lightbulb
import toolbox

from components.views import GreetingMessageView
from core.consts import ALLOWED_GREETING_VARS_STR, Color
from core.objects import GreetingsData
from core.utils import Hook, Plugin, format_greeting

if typing.TYPE_CHECKING:
    from core.bot import Anya


@lightbulb.Check
async def ensure_existence(context: lightbulb.Context | hikari.Member) -> bool:
    await plugin.bot.db.pool.execute(  # type: ignore
        """
        INSERT INTO greetings
        VALUES ( $1 )
        ON CONFLICT DO NOTHING;
        """,
        context.guild_id,
    )
    return True


plugin = Plugin("greetings", "Greet your users!", 3)
plugin.add_checks(ensure_existence | lightbulb.checks.has_guild_permissions(hikari.Permissions.MANAGE_GUILD))


@plugin.command
@lightbulb.command("greetings", "Add welcome/leave configs.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def greetings(_):
    ...


@greetings.child
@lightbulb.option(
    "channel", "Channel for messages.", type=hikari.GuildChannel, channel_types=[hikari.ChannelType.GUILD_TEXT]
)
@lightbulb.option("category", "Greeting category to set channel for.", choices=["welcome", "goodbye"])
@lightbulb.command("channel", "Channel for welcome/leave messages.", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def channel(context: lightbulb.SlashContext, channel: hikari.InteractionChannel, category: str) -> None:
    await context.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    member = (bot := plugin.bot).cache.get_member(
        context.guild_id or 0, bot.get_me()
    ) or await context.bot.rest.fetch_my_member(context.guild_id or 0)
    guild = context.get_guild() or await plugin.bot.rest.fetch_guild(context.guild_id or 0)
    _channel: hikari.PermissibleGuildChannel = guild.get_channel(
        channel.id
    ) or await plugin.bot.rest.fetch_channel(  # type: ignore
        channel.id
    )
    perms = toolbox.calculate_permissions(member=member, channel=_channel)
    if not (perms & hikari.Permissions.SEND_MESSAGES and perms & hikari.Permissions.EMBED_LINKS):
        await context.interaction.edit_initial_response(
            embed=plugin.bot.fail_embed("Bot is missing required permissions (send message, embed links).")
        )
        return
    await plugin.bot.db.pool.execute(  # type: ignore
        f"UPDATE greetings SET {category}_channel_id = $1 WHERE guild_id = $2",
        channel.id,
        context.guild_id,
    )

    await context.interaction.edit_initial_response(
        embed=plugin.bot.success_embed(f"Set {category} channel to {channel.mention} ({channel.name})")
    )


@greetings.child
@lightbulb.option("color", "New embed accent color.", required=False)
@lightbulb.option("ignore_bots", "Set to True to ignore messages for bot users.", bool, required=False)
@lightbulb.command("basic_config", "Edit the base server config for greetings.", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def configs(context: lightbulb.SlashContext, ignore_bots: bool | None, color: str | None) -> None:
    pool = plugin.bot.db.pool
    if not any((color, ignore_bots)):
        await context.respond("You need to provide atleast one argument.", flags=hikari.MessageFlag.EPHEMERAL)
        return
    if all((ignore_bots, color)):
        await pool.execute(  # type: ignore
            "UPDATE greetings SET accent_color = $1, ignore_bots = $2 WHERE guild_id = $3 ",
            int(hikari.Color.from_hex_code(color or "")),
            ignore_bots,
            context.guild_id,
        )
    elif color is not None:
        await pool.execute(  # type: ignore
            "UPDATE greetings SET accent_color = $1 WHERE guild_id = $2",
            int(hikari.Color.from_hex_code(color)),
            context.guild_id,
        )
    elif ignore_bots is not None:
        await pool.execute(  # type: ignore
            "UPDATE greetings SET ignore_bots = $1 WHERE guild_id = $2",
            ignore_bots,
            context.guild_id,
        )
    configs = GreetingsData(
        **dict(await pool.fetchrow("SELECT * FROM greetings WHERE guild_id = $1", context.guild_id))  # type: ignore
    )
    await context.respond(
        embed=plugin.bot.success_embed(
            (
                f"**Updated configs:**\n\n`color`: {configs.accent_color}\n`ignore_bots`: {configs.ignore_bots}"
                "\nFor full config details use `/greetings configs`"
            )
        )
    )


@greetings.child
@lightbulb.command("configs", "Check server's greetings configs.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def configs_cmd(context: lightbulb.SlashContext) -> None:
    # fmt: off
    configs = GreetingsData(
        **dict(await plugin.bot.db.pool.fetchrow("SELECT * FROM greetings WHERE guild_id = $1",  # type: ignore
        context.guild_id))  
    )
    # fmt: on
    guild = context.get_guild() or await plugin.bot.rest.fetch_guild(context.guild_id or 0)
    embed = (
        hikari.Embed(
            description="\n".join(
                [
                    f"`Server ID`: {configs.guild_id}",
                    f"`Ignore Bots`: {configs.ignore_bots}",
                    f"`Embed accent color`: {hikari.Color.from_int(configs.accent_color)}",
                    f"`Welcome channel`: {f'<#{configs.welcome_channel_id}>' if configs.welcome_channel_id else None}",
                    f"`Leave channel`: {f'<#{configs.goodbye_channel_id}>' if configs.goodbye_channel_id else None}",
                    "- The embed color in this message is same as the greeting's accent color",
                    "- Use `/greetings mock` command to check welcome/goodbye messages.",
                ]
            ),
            color=configs.accent_color,
        )
        .set_author(name=f"Greeting Configs for {guild.name}")
        .set_thumbnail(guild.icon_url)
    )
    await context.respond(embed=embed)


@greetings.child
@lightbulb.option("category", "Greeting category to set channel for.", choices=["welcome", "goodbye"])
@lightbulb.command("message", "Update greeting message", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def message(context: lightbulb.SlashContext, category: typing.Literal["welcome", "goodbye"]) -> None:

    res = await context.respond(
        embed=hikari.Embed(description=f"**Allowed Variables:**\n{ALLOWED_GREETING_VARS_STR}", color=Color.ANYA),
        components=(view := GreetingMessageView(category)).build(),
        flags=hikari.MessageFlag.EPHEMERAL,
    )
    await view.start(res)
    await view.wait()
    await context.interaction.edit_initial_response(components=[])


@greetings.child
@lightbulb.option("category", "Greeting category to set channel for.", choices=["welcome", "goodbye"])
@lightbulb.command("mock", "Mock a welcome or goodbye.", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def mock(context: lightbulb.SlashContext, category: typing.Literal["welcome", "goodbye"]) -> None:
    member: hikari.Member = context.member or await plugin.bot.rest.fetch_member(
        context.guild_id or 0, context.author.id
    )

    event = (
        hikari.MemberCreateEvent(shard=context.event.shard, member=member)
        if category == "welcome"
        else hikari.MemberDeleteEvent(
            shard=context.event.shard, guild_id=context.guild_id or hikari.Snowflake(0), user=member, old_member=member
        )
    )
    plugin.bot.dispatch(event)


@plugin.listener(hikari.MemberCreateEvent)
async def new_member(event: hikari.MemberCreateEvent) -> None:
    # fmt: off
    configs = GreetingsData(
        **dict(await plugin.bot.db.pool.fetchrow("SELECT * FROM greetings WHERE guild_id = $1",  # type: ignore
        event.guild_id))  
    )
    # fmt: on
    if configs.welcome_channel_id is not None:
        try:
            await plugin.bot.rest.create_message(
                configs.welcome_channel_id,
                embed=hikari.Embed(
                    description=format_greeting(
                        configs.welcome_message,
                        event.user,
                        event.get_guild() or await plugin.bot.rest.fetch_guild(event.guild_id),
                    ),
                    color=configs.accent_color,
                )
                .set_author(name=str(event.member))
                .set_thumbnail(event.member.display_avatar_url),
            )
        except hikari.HTTPError:
            ...


@plugin.listener(hikari.MemberDeleteEvent)
async def left_member(event: hikari.MemberDeleteEvent) -> None:
    # fmt: off
    configs = GreetingsData(
        **dict(await plugin.bot.db.pool.fetchrow("SELECT * FROM greetings WHERE guild_id = $1",  # type: ignore
        event.guild_id))  
    )
    # fmt: on
    if configs.welcome_channel_id is not None:
        try:
            await plugin.bot.rest.create_message(
                configs.welcome_channel_id,
                embed=hikari.Embed(
                    description=format_greeting(
                        configs.welcome_message,
                        event.user,
                        event.get_guild() or await plugin.bot.rest.fetch_guild(event.guild_id),
                    ),
                    color=configs.accent_color,
                )
                .set_author(name=str(event.user))
                .set_thumbnail(event.user.display_avatar_url),
            )
        except hikari.HTTPError:
            ...


@Hook.create("greetings:loader")
def load(bot: Anya) -> None:
    bot.add_plugin(plugin)
    if bot.hooks.get("greetings:loader") is None:
        bot.hooks["greetings:loader"] = load
