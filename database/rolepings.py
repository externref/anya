from __future__ import annotations
import typing

import aiomysql
import lightbulb


class RolePingHandler:
    """
    Class managing the role pings for card spawns

    Attributes
    ----------

        database_pool: :class:`aiomysql.Pool`
            The pool passed by the `.Bot` class for this class to function.
        tier_1_cache: :class:`dict[int, int]`
            Cache for tier 1 roles.
        tier_2_cache: :class:`dict[int, int]`
            Cache for tier 2 roles.
        tier_3_cache: :class:`dict[int, int]`
            Cache for tier 3 roles.
        tier_4_cache: :class:`dict[int, int]`
            Cache for tier 4 roles.
        tier_5_cache: :class:`dict[int, int]`
            Cache for tier 5 roles.
        tier_6_cache: :class:`dict[int, int]`
            Cache for tier 6 roles.

    """

    database_pool: aiomysql.Pool
    tier_1_cache: dict[int, int] = {}
    tier_2_cache: dict[int, int] = {}
    tier_3_cache: dict[int, int] = {}
    tier_4_cache: dict[int, int] = {}
    tier_5_cache: dict[int, int] = {}
    tier_6_cache: dict[int, int] = {}

    async def setup(self, bot: lightbulb.BotApp) -> aiomysql.Pool:
        """
        Setting up this database class for usage.

        Paramaters
        ----------

            bot: :class:`lightbulb.BotApp`
                The bot class this prefix class is for.

        Returns
        -------

            :class:`aiomysql.Pool`

        """

        async with bot.database_pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS rolepings
                    ( 
                        guild_id BIGINT, 
                        tier_1 BIGINT, 
                        tier_2 BIGINT, 
                        tier_3 BIGINT, 
                        tier_4 BIGINT, 
                        tier_5 BIGINT, 
                        tier_6 BIGINT
                    ) ;
                    """
                )
            await conn.commit()
        self.database_pool = bot.database_pool
        return bot.database_pool

    async def get_role(self, tier: int, guild_id: int) -> int | None:
        """
        Get role ID for the pings upon spawn.

        Paramaters
        ----------

            tier: :class:`int`
                Tier for which to get role.
            guild_id: :class:`int`
                Server ID to get role for.

        Returns
        -------

            :class:`typing.Optional[int]`

        """
        cache_data: dict[int, int] = getattr(self, f"tier_{tier}_cache")
        cache = cache_data.get(guild_id)
        if cache is not None:
            return cache

        async with self.database_pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute(
                    f"""
                    SELECT tier_{tier}
                    FROM rolepings
                    WHERE guild_id = %s
                    """,
                    (guild_id,),
                )

                data = await cursor.fetchone()

        if data:
            cache_data[guild_id] = data[0]
            return data[0]

    async def set_role(self, guild_id: int, tier: int, role_id: int) -> None:
        """
        Setting roles for card spawn pings.

        Paramaters
        ----------

            guild_id: :class:`int`
                Server ID to set role for.
            tier: :class:`int`
                Tier for which to set role.
            role_id: :class:`int`
                ID of the role to ping.

        """
        async with self.database_pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute(
                    f"""
                    INSERT INTO rolepings
                    ( guild_id, tier_{tier} )
                    VALUES ( %s, %s )
                    """,
                    (guild_id, role_id),
                )

            await conn.commit()
