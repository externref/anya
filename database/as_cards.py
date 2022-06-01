import datetime

import aiomysql
import lightbulb


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


class ShoobCardDatabase:
    database_pool: aiomysql.Pool

    async def setup(self, bot: lightbulb.BotApp) -> aiomysql.Pool:
        """
        Setting up this database class for usage.

        Paramaters
        ----------

            bot: :class:`lightbulb.BotApp`
                The bot class this class is for.

        Returns
        -------

            :class:`aiomysql.Pool`

        """
        db_pool = bot.database_pool

        async with db_pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS cardspawns
                    (
                        guild_id BIGINT,
                        spawn_ts BIGINT,
                        card_name VARCHAR(40),
                        tier INT,
                        card_url VARCHAR(100),
                        card_v BIGINT,
                        claimer_id BIGINT
                    );
                    """
                )

            await conn.commit()
        self.database_pool = db_pool
        return self.database_pool

    async def insert_spawn_data(
        self,
        guild_id: int,
        spawn_ts: int,
        card_name: str,
        card_url: str,
        tier: int,
        card_v: int | None = None,
        claimer_id: int | None = None,
    ) -> None:
        """
        Inserting new card spawn and claim data in the database.

        Paramaters
        ----------

            guild_id: :class:`int`
                ID of the guild where card spawned
            spawn_ts :class:`int`
                Timestamp of time at which the card was claimed
            card_name: :class:`str`
                Name of the card
            tier: :class:`int`
                Tier of the card that got spawned
            card_v: :class:`int`
                Version of the card
            claimer_id :class:`typing.Optional[int]
                ID of the user who claimed the card


        """
        async with self.database_pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute(
                    """
                    INSERT INTO cardspawns
                    VALUES ( %s, %s, %s,%s, %s, %s, %s )
                    """,
                    (guild_id, spawn_ts, card_name, card_url, tier, card_v, claimer_id),
                )
            await conn.commit()

    async def recent_guild_spawns(self, guild_id, limit=5) -> list[CardSpawn]:
        """Getting recent spawns in the server.

        Paramaters
        ----------

            guild_id: :class:`int`
                ID of the server.
            limit: :class:`int`
                Max number of card data to get.

        Returns
        -------

            :class:`CardSpawn`

        """
        async with self.database_pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute(
                    """
                    SELECT * FROM cardspawns
                    WHERE guild_id = %s
                    ORDER BY spawn_ts DESC
                    """,
                    (guild_id,),
                )
                data_list: list = await cursor.fetchmany(limit)

        return [CardSpawn(data) for data in data_list if data]

    async def recent_guild_claims(self, guild_id: int, limit=5) -> list[CardSpawn]:
        """Getting recent claims in the server.

        Paramaters
        ----------

            guild_id: :class:`int`
                ID of the server.
            limit: :class:`int`
                Max number of card data to get.

        Returns
        -------

            :class:`CardSpawn`

        """
        async with self.database_pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute(
                    """
                    SELECT * FROM cardspawns
                    WHERE guild_id = %s AND claimer_id IS NOT NULL
                    ORDER BY spawn_ts DESC
                    """,
                    (guild_id,),
                )
                data_list: list = await cursor.fetchmany(limit)

        return [CardSpawn(data) for data in data_list if data]

    async def recent_guild_despawns(
        self, guild_id: int, limit: int = 5
    ) -> list[CardSpawn]:
        """Getting recent despawns in the server.

        Paramaters
        ----------

            guild_id: :class:`int`
                ID of the server.
            limit: :class:`int`
                Max number of card data to get.

        Returns
        -------

            :class:`CardSpawn`

        """
        async with self.database_pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute(
                    """
                    SELECT * FROM cardspawns
                    WHERE guild_id = %s AND claimer_id IS NULL
                    ORDER BY spawn_ts DESC
                    """,
                    (guild_id,),
                )
                data_list: list = await cursor.fetchmany(limit)
        return [CardSpawn(data) for data in data_list if data]

    async def recent_tier_spawns(
        self, guild_id: int, tier: int, limit: int = 5
    ) -> list[CardSpawn]:
        """Getting recent spawns of a tier in the server.

        Paramaters
        ----------

            guild_id: :class:`int`
                ID of the server.
            tier: :class:`int`
                Tier to get spawns for
            limit: :class:`int`
                Max number of card data to get.

        Returns
        -------

            :class:`CardSpawn`

        """
        async with self.database_pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute(
                    """
                    SELECT * FROM cardspawns
                    WHERE guild_id = %s AND tier = %s
                    ORDER BY spawn_ts DESC
                    """,
                    (guild_id, tier),
                )
                data_list: list = await cursor.fetchmany(limit)
        return [CardSpawn(data) for data in data_list if data]
