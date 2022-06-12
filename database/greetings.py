from __future__ import annotations


import aiomysql
import hikari

from core.objects import Greeting


class GreetingsHandler:
    """
    Class dealing with greetings in bot's servers.
    Includes Leave and join module functions.
    """

    database_pool: aiomysql.Pool
    bot: hikari.GatewayBot

    async def setup(self, bot: hikari.GatewayBot) -> aiomysql.Pool:
        """
        Setting up this database class for usage.

        Paramaters
        ----------

            bot: :class:`hikari.GatewayBot`
                The bot class this class is for.

        Returns
        -------

            :class:`aiomysql.Pool`

        """
        db_pool: aiomysql.Pool = bot.database_pool
        async with db_pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS greetings
                    (   
                        guild_id BIGINT,

                        welcome_cid BIGINT,
                        welcome_message TEXT,
                        welcome_color INT,
                        welcome_image_bytes BLOB,
                        welcome_embed INT,

                        goodbye_cid BIGINT,
                        goodbye_message TEXT,
                        goodbye_color INT,
                        goodbye_image_bytes BLOB,
                        goodbye_embed INT
                        
                    )
                    """
                )
            await conn.commit()
        self.database_pool = db_pool
        self.bot = bot

    async def exec_write_query(self, query: str, data: tuple) -> None:
        async with self.database_pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute(query, data)
            await conn.commit()

    async def get_greeting_data_for(
        self, greeting: str, guild_id: int
    ) -> None | Greeting:
        async with self.database_pool.acquire() as connection:
            connection: aiomysql.Connection
            async with connection.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute(
                    f"""
                    SELECT guild_id, {greeting}_cid, {greeting}_message, {greeting}_color, {greeting}_image_bytes, {greeting}_embed 
                    FROM greetings
                    WHERE guild_id = %s
                    """,
                    (guild_id,),
                )

        data = await cursor.fetchone()
        if not data:
            return None
        return Greeting(self.bot, data)

    async def set_welcome_data_for_guild(self, guild_id: int, channel_id: int) -> None:
        await self.exec_write_query(
            """
            INSERT INTO greetings
            ( guild_id, welcome_cid, welcome_message, welcome_embed )
            VALUES ( %s, %s, %s, %s )
            """,
            (guild_id, channel_id, "Hey $user, welcome to $server.", 0),
        )

    async def set_goodbye_data_for_guild(self, guild_id: int, channel_id: int) -> None:
        await self.exec_write_query(
            """
            INSERT INTO greetings
            ( guild_id, goodbye_cid, goodbye_message, goodbye_embed )
            VALUES ( %s, %s, %s, %s )
            """,
            (guild_id, channel_id, "$user left the server.", 0),
        )

    async def update_channel_for(
        self, greeting: str, guild_id: int, channel_id: int
    ) -> None:
        await self.exec_write_query(
            f"""
            UPDATE greetings SET 
            {greeting}_cid = %s
            WHERE guild_id = %s
            """,
            (channel_id, guild_id),
        )

    async def update_message_for(
        self, greeting: str, guild_id: int, message: str
    ) -> None:
        await self.exec_write_query(
            f"""
            UPDATE greetings SET 
            {greeting}_message = %s
            WHERE guild_id = %s
            """,
            (message, guild_id),
        )

    async def update_color_for(self, greeting: str, guild_id: int, hex: int) -> None:
        await self.exec_write_query(
            f"""
            UPDATE greetings SET
            {greeting}_color = %s
            WHERE guild_id = %s
            """,
            (hex, guild_id),
        )

    async def set_image_for(
        self, greeting: str, guild_id: int, image_data: bytes
    ) -> None:
        await self.exec_write_query(
            f"""
            UPDATE greetings SET
            {greeting}_image = %s
            WHERE guild_id = %s
            """,
            (image_data, guild_id),
        )
