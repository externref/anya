from __future__ import annotations

import asyncio
import os

import aiomysql
import dotenv
import hikari
import lightbulb
from database.prefixes import PrefixDatabase

from .colors import Colors


class Bot(lightbulb.BotApp):
    """
    The bot class which is a subclass of `lightbulb.BotApp` & `hikari.GatewayBot` class.
    All the basic bot related setups are done here.

    Attributes
    ----------

        colors: :class:`Colors`
            Color helper class
        database_pool: :class:`aiomysql.Pool`
            MySQL databse pool to work with the databases
        prefix_db: :class:`PrefixDatabase`
            Prefix managing class

    """

    colors: Colors
    database_pool: aiomysql.Pool
    prefix_db: PrefixDatabase

    def __init__(self) -> None:
        dotenv.load_dotenv()  # loading enviromental variables in the project
        super().__init__(
            token=os.getenv("TOKEN"),
            prefix=self.get_prefix,  # dynamic `get_prefix` function
            intents=hikari.Intents(
                hikari.Intents.ALL_UNPRIVILEGED
                | hikari.Intents.ALL_MESSAGES  # adding message intents
            ),
        )
        self.colors = Colors()  # initalising custom colors class
        self.prefix_db = (
            PrefixDatabase()
        )  # initialising PrefixDatabase, setup will be called later
        self.load_extensions_from("extensions")  # loading all bot extensions
        self.event_manager.subscribe(
            hikari.StartedEvent, self.get_databases_ready
        )  # triggering an coroutine on hikari.StartedEvent

    async def get_databases_ready(self, event: hikari.StartedEvent) -> None:
        """
        This function is called when the bot is Started
        All the database related setups are performed here.

        Parameters
        ----------

        event: :class:`hikari.StartedEvent`
            The event reponsible for triggering this coro.

        """
        self.database_pool: aiomysql.Pool = await aiomysql.create_pool(
            host=os.getenv("MYSQLHOST"),
            user=os.getenv("MYSQLUSER"),
            db=os.getenv("MYSQLDATABASE"),
            password=os.getenv("MYSQLPASSWORD"),
            port=os.getenv("MYSQLPORT"),
            loop=asyncio.get_event_loop(),
            autocommit=False,
        )  # getting configs from the .env file and setting up the database
        await self.prefix_db.setup(
            self
        )  # this function adds all important attributes to the PrefixDatabase class

    async def get_prefix(self, bot: "Bot", message: hikari.Message) -> str:
        """
        Getting custom prefixes for the server or returning the default one
        if None is set.

        Parameters
        ----------

        bot: :class:`.Bot`
            The bot class this coroutine is for.
        message: :class:`hikari.Message`
            The message which triggered the coroutine.

        Returns
        -------

        :class:`str`

        """
        return await self.prefix_db.get_prefix_by_id(message.guild_id)
