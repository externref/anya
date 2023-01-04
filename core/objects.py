from __future__ import annotations

import attrs


@attrs.define(kw_only=True)
class GreetingsData:
    guild_id: int
    ignore_bots: bool
    accent_color: int
    welcome_message: str
    goodbye_message: str
    welcome_channel_id: int | None
    goodbye_channel_id: int | None
