from __future__ import annotations

import asyncio
import os
import datetime

import aiomysql
import dotenv
import hikari
import lightbulb
from database.as_cards import ShoobCardDatabase
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
            prefix=lightbulb.when_mentioned_or(
                self.get_prefix
            ),  # dynamic `get_prefix` function
            intents=hikari.Intents(
                hikari.Intents.ALL_UNPRIVILEGED
                | hikari.Intents.ALL_MESSAGES  # adding message intents
            ),
            help_slash_command=True,
        )
        self.colors = Colors()  # initalising custom colors class
        self.prefix_db = (
            PrefixDatabase()
        )  # initialising PrefixDatabase, setup will be called later
        self.cards_db = ShoobCardDatabase()  # initialising class for shoob bot cards
        self.load_extensions_from("extensions")  # loading all bot extensions
        self.load_extensions("lightbulb.ext.filament.exts.superuser")
        self.event_manager.subscribe(
            hikari.StartingEvent, self.get_databases_ready
        )  # triggering an coroutine on hikari.StartedEvent

    async def get_databases_ready(self, event: hikari.StartingEvent) -> None:
        """
        This function is called when the bot is Started
        All the database related setups are performed here.

        Parameters
        ----------

        event: :class:`hikari.StartedEvent`
            The event reponsible for triggering this coro.

        """
        self.start_time: datetime.datetime = datetime.datetime.now()
        self.database_pool: aiomysql.Pool = await aiomysql.create_pool(
            host=os.getenv("MYSQLHOST"),
            user=os.getenv("MYSQLUSER"),
            db=os.getenv("MYSQLDATABASE"),
            password=os.getenv("MYSQLPASSWORD"),
            port=int(os.getenv("MYSQLPORT")),
            loop=asyncio.get_event_loop(),
            autocommit=False,
        )  # getting configs from the .env file and setting up the database
        await self.prefix_db.setup(
            self
        )  # this function adds all important attributes to the PrefixDatabase class
        await self.cards_db.setup(
            self
        )  # addding table to the database if it already doesnt exist.

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
        return await self.prefix_db.get_prefix_by_id(message.guild_id) or "anya"

    @property
    def invite_url(self) -> str:
        """Invite url for the bot."""
        return (
            f"https://discord.com/api/oauth2/authorize?client_id={self.get_me().id}"
            "&permissions=378025593921&scope=bot%20applications.commands"
        )

    @property
    def uptime(self) -> datetime.timedelta:
        """Returns a `datetime.timedelta` with the bot's uptime"""
        return datetime.datetime.now() - self.start_time
