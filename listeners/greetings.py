from __future__ import annotations
from email import message

import hikari
import lightbulb
from core.bot import Bot


class Plugin(lightbulb.Plugin):
    def __init__(self) -> None:
        super().__init__("Greetings listener")
        self.ignored = True
        self.bot: Bot


plugin = Plugin()


def parse_member_message(base_message: str, member: hikari.Member) -> str:
    """A function parsing message for greeting events in a guild.

    Paramaters
    ----------

        base_message: :class:`str`
            Message to parse from.
        member: :class:`hikari.Member`
            The member which was added/removed from the guild.

    Returns
    -------

        :class:`str`

    """
    format_ = {
        "$user": str(member),
        "$username": member.username,
        "$id": member.id,
        "$discrim": member.discriminator,
        "$server": member.get_guild().name,
        "$joined_on": member.joined_at,
        "$joined_discord": member.created_at,
        "$bot": member.is_bot,
    }
    for key, value in format_.items():
        base_message.replace(key, str(value))

    return base_message


@plugin.listener(hikari.MemberCreateEvent)
async def member_added_to_server(event: hikari.MemberCreateEvent) -> None:
    """This event is triggered when a new member is added to the guild.

    Paramaters
    ----------

        event: :class:`hikari.MemberCreateEvent`
            The event responsible for triggering this function.

    """
    data = await plugin.bot.greeting_db.get_greeting_data_for("welcome", event.guild_id)
    if not data:
        return
    else:
        channel = data.channel
        message = parse_member_message(data.message, event.member)
        image_file = data.welcome_bytes
        embed_color = data.color
        to_embed = data.is_embed

    if not data.channel:
        return

    if to_embed:
        embed = hikari.Embed(color=embed_color or 0, description=message)

        embed.set_author(
            name=str(event.member),
            icon=event.member.avatar_url or event.member.default_avatar_url,
        )
        if image_file:
            embed.set_image(image_file)
        await plugin.bot.rest.create_message(channel.id, embed=embed)

    else:
        await plugin.bot.rest.create_message(
            channel.id, message, attachments=[image_file] if image_file else []
        )


def load(bot: Bot) -> None:
    bot.add_plugin(plugin)


def unload(bot: Bot) -> None:
    bot.remove_plugin(plugin)
