from __future__ import annotations

import attrs


@attrs.define(kw_only=True)
class GreetingsData:
    guild_id: int
    ignore_bots: bool
    accent_color: int
    welcome_message: str | None
    goodbye_message: str | None
    welcome_channel_id: int | None
    goodbye_channel_id: int | None
