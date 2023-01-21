import typing

import hikari

INVITE_URL = "https://discord.com/api/oauth2/authorize?client_id=979906554188939264&permissions={perms}&scope=bot%20applications.commands"  # noqa: e501


@typing.final
class Color:
    ANYA = hikari.Color.from_int(0xFADFAD)
    GREEN = hikari.Color.from_int(0x2ECC71)
    RED = hikari.Color.from_int(0xE74C3C)


@typing.final
class Emojis:
    PREVIOUS = hikari.CustomEmoji.parse("<:previous:1066275900473233489>")
    NEXT = hikari.CustomEmoji.parse("<:next:1066276075023384586>")
    DUSTBIN = hikari.CustomEmoji.parse("<:dustbin:1066277926347218964>")
    HOME = hikari.CustomEmoji.parse("<:home:1066250458089410630>")


@typing.final
class Chars:
    PING_PONG = "\U0001f3d3"
    DIAMOND_DOT = "\U0001f4a0"
    SUCCESS = "\u2705"
    FAIL = "\u274c"
    TICK = SUCCESS
    CROSS = FAIL


class ImageURLs:
    BANNER = "https://i.imgur.com/bTPsA9q.png"
    INVITE = "https://i.imgur.com/PzH7LYF.png"
    COMMANDS = "https://i.imgur.com/c48SdPK.png"


ALLOWED_GREETING_VARS_STR: str = "\n".join(
    ALLOWED_GREETING_VARS := [
        "member",
        "member_name",
        "member_disriminator",
        "member_id",
        "member_avatar",
        "member_creation_timestamp",
        "current_timestamp",
        "server_name",
        "member_count",
    ]
)
