import datetime

import hikari


class Greeting:
    """
    Object construtor for data fetched from the MySQL database.

    Paramaters
    ----------

        bot: :class:`hikari.GatewayBot`
            The bot class to make this class for.
        data: :class:`tuple`
            Raw tuple response from the database.

    """

    def __init__(self, bot: hikari.GatewayBot, data: tuple[str | int | bytes]) -> None:
        self.data = data
        self.bot = bot

    @property
    def channel(self) -> hikari.GuildTextChannel:
        return self.bot.cache.get_guild(self.data[0]).get_channel(self.data[1])

    @property
    def message(self) -> str:
        return self.data[2]

    @property
    def color(self) -> hikari.Color:
        return hikari.Color(self.data[3])

    @property
    def welcome_bytes(self) -> hikari.Bytes | None:
        return hikari.Bytes(self.data[4]) if self.data[4] else None

    @property
    def is_embed(self) -> bool:
        return True if self.data[5] == 1 else False


class CardSpawn:
    def __init__(self, data_tuple) -> None:
        self.data = data_tuple

    @property
    def guild_id(self) -> int:
        return self.data[0]

    @property
    def spawn_ts(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.data[1])

    @property
    def name(self) -> str:
        return self.data[2]

    @property
    def tier(self) -> int:
        return self.data[3]

    @property
    def url(self) -> str:
        return self.data[4]

    @property
    def v(self) -> int:
        return self.data[5]

    @property
    def claimer_id(self) -> int:
        return self.data[6]
