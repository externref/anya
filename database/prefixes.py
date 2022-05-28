from __future__ import annotations

import aiomysql
import lightbulb


class PrefixDatabase:
    """
    Class for managing server custom prefixes.

    Attributes
    ----------

        database_poll: :class:`aiomysql.Poll`
            The pool passed by the `.Bot` class for this class to function.
        prefix_cache: :class:`dict[int, str]`
            A dictionary with guild_id to prefix key, value pair.

    """

    database_pool: aiomysql.Pool
    prefix_cache: dict[str, str] = {}

    async def setup(self, bot: lightbulb.BotApp) -> aiomysql.Pool:
        """
        Setting up this database class for usage.

        Paramaters
        ----------

            bot: :class:`hikari.GatewayBot`
                The bot class this prefix class is for.

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
                    CREATE TABLE IF NOT EXISTS prefixes
                    ( guild_id BIGINT, prefix VARCHAR (10) );
                    """
                )

            await conn.commit()
        self.database_pool = db_pool
        return self.database_pool

    async def get_prefix_by_id(self, guild_id: int) -> str:
        """
        Getting the prefix for the guild whose id is provided.

        This method look-ups into the cache first, if the prefix is not found in cache
        the method fetchs it from the database, and adds it to the cache

        Paramaters
        ---------

            guild_id: :class:`int`
                Guild ID for which prefix is needed.

        Returns
        -------

            :class:`str`

        """
        cache = self.prefix_cache.get(guild_id)
        if cache:
            return cache
        async with self.database_pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
                    SELECT * FROM prefixes
                    WHERE guild_id = %s;
                    """,
                    (guild_id,),
                )
                data = await cursor.fetchone()
        if data:
            self.prefix_cache[guild_id] = data[1]
            return data[1]  # cache-ing and returning custom prefix
        else:
            self.prefix_cache[guild_id] = "a!"
            return "a!"  # cache-ing and returning default prefix

    async def set_prefix(self, guild_id: int, prefix: str) -> None:
        """
        Method used to update/set prefix for a server.

        This adds the updated prefix both in the cache and the database.

        Paramaters
        ----------

            guild_id: :class:`int`
                ID of the guild to update prefix of
            prefix: :class:`str`
                The new prefix

        """
        self.prefix_cache[guild_id] = prefix  # updating the prefix in cache
        async with self.database_pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                if await self.get_prefix_by_id(guild_id):
                    await cursor.execute(
                        """
                        UPDATE prefixes
                        SET prefix = %s
                        WHERE guild_id = %s;
                        """,
                        (prefix, guild_id),
                    )
                else:
                    await cursor.execute(
                        """
                        INSERT INTO prefixes
                        VALUES ( %s , %s );
                        """,
                        (guild_id, prefix),
                    )
            await conn.commit()
