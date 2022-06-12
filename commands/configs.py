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


@plugin.command
@lightbulb.command(
    name="welcome", description="Welcome settings for this server.", aliases=["welc"]
)
@lightbulb.implements(lightbulb.PrefixCommandGroup, lightbulb.SlashCommandGroup)
async def welcome(_: lightbulb.PrefixContext | lightbulb.SlashContext) -> None:
    """
    Welcome commands to greet your new members!

    - This sub-module has 5 customisations: `channel`, `message`, `color`, `image` & `embed`

    Use `anya welcome <subcommand>` for more information.

    **Example Usage:** `anya welcome channel #entry`

    """
    pass


@plugin.command
@lightbulb.command(
    name="goodbye",
    description="Goodbye message settings for this server.",
    aliases=["gb"],
)
@lightbulb.implements(lightbulb.PrefixCommandGroup, lightbulb.SlashCommandGroup)
async def goodbye(_: lightbulb.PrefixContext | lightbulb.SlashContext) -> None:
    """
    A log of users who left the server ig?

    - This sub-module has 5 customisations: `channel`, `message`, `color`, `image` & `embed`

    Use `anya goodbye <subcommand>` for more information.

    **Example Usage:** `anya goodbye channel #left-users`

    """
    pass


async def set_channel(
    context: lightbulb.Context,
    greeting: str,
    channel: hikari.GuildTextChannel,
) -> None:
    """Helper function for commands used for setting greeting channels.

    Paramaters
    ----------

        context: :class:`lightbulb.Context`
            The context which awaited this coro.
        greeting: :class:`str`
            Type of greeting.
        channel: :class:`hikari.GuildTextChannel`
            The new channel to setup for greetings.

    """
    data = await plugin.bot.greeting_db.get_greeting_data_for(
        greeting, context.guild_id
    )
    if not data:
        await plugin.bot.greeting_db.set_welcome_data_for_guild(
            context.guild_id, channel.id
        )
    else:
        await plugin.bot.greeting_db.update_channel_for(
            greeting, context.guild_id, channel.id
        )

    await context.respond(
        embed=hikari.Embed(
            description=f"Set {greeting} channel to **{channel.name}** (<#{channel.id}>",
            color=plugin.bot.colors.peach_yellow,
        ),
        reply=True,
    )


@welcome.child
@lightbulb.option(
    name="channel",
    description="The channel to use.",
    type=hikari.TextableGuildChannel,
    channel_types=[hikari.ChannelType.GUILD_TEXT],
)
@lightbulb.command(
    name="channel",
    description="Channel where all the welcome messages would be sent.",
    pass_options=True,
)
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def w_channel(
    context: lightbulb.PrefixContext | lightbulb.SlashContext,
    channel: hikari.GuildTextChannel,
) -> None:
    """This command is used to setup a welcome channel for new members.

    **Allowed Arguments:**
    `channel`: The new welcome channel.

    **Example Usage:** `anya welcome channel #hello`

    """
    await set_channel(context, "welcome", channel)


@goodbye.child
@lightbulb.option(
    name="channel",
    description="The channel to use.",
    type=hikari.TextableGuildChannel,
    channel_types=[hikari.ChannelType.GUILD_TEXT],
)
@lightbulb.command(
    name="channel",
    description="Channel where all the goodbye messages would be sent.",
    pass_options=True,
)
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def g_channel(
    context: lightbulb.PrefixContext | lightbulb.SlashContext,
    channel: hikari.GuildTextChannel,
) -> None:
    """
    Setting up a log channel for users who left the server.

    **Allowed Arguments:**
    `channel`: The channel to send logs in.

    **Example Usage:** `anya goodbye channel #bye`
    """
    await set_channel(context, "goodbye", channel)


async def set_message(context: lightbulb.Context, greeting: str, message: str) -> None:
    await plugin.bot.greeting_db.update_message_for(greeting, context.guild_id, message)
    await context.respond(
        embed=hikari.Embed(
            description=message, color=plugin.bot.colors.green
        ).set_author(name="Set welcome message to:"),
        reply=True,
    )


@welcome.child
@lightbulb.option(
    name="message",
    description="Enter the message to send",
    modifier=lightbulb.OptionModifier.CONSUME_REST,
)
@lightbulb.command(
    name="message",
    description="The message to send when a new member joins",
    pass_options=True,
)
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def w_message(
    context: lightbulb.PrefixContext | lightbulb.SlashContext,
    channel: hikari.GuildTextChannel,
) -> None:
    """
    Use this command to customise the welcome message.

    **Allowed Arguments:**
    `message`: The new message.

    **Example Usage:** : `anya welcome message Hello $user, welcome to $server.`
    """
    await set_channel(context, "welcome", channel)


@goodbye.child
@lightbulb.option(
    name="message",
    description="Enter the message to send",
    modifier=lightbulb.OptionModifier.CONSUME_REST,
)
@lightbulb.command(name="message", description="The log message.", pass_options=True)
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def g_message(
    context: lightbulb.PrefixContext | lightbulb.SlashContext,
    channel: hikari.GuildTextChannel,
) -> None:
    """
    Use this command to customise the log message sent upon a member leaving the server.

    **Allowed Arguments:**
    `message`: The new message.

    **Example Usage:** : `anya goodbye message $user left us.`
    """
    await set_channel(context, "goodbye", channel)


def load(bot: Bot) -> None:
    bot.add_plugin(plugin)


def unload(bot: Bot) -> None:
    bot.remove_plugin(plugin)
