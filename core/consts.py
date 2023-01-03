import typing

import hikari

INVITE_URL = "https://discord.com/api/oauth2/authorize?client_id=979906554188939264&permissions={perms}&scope=bot%20applications.commands"


@typing.final
class Color:
    ANYA = hikari.Color.from_int(0xFADFAD)
    GREEN = hikari.Color.from_int(0x2ECC71)
    RED = hikari.Color.from_int(0xE74C3C)


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
