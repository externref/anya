from __future__ import annotations

import importlib
import os
import typing

import hikari
import lightbulb
import miru

from core.consts import Chars, Color
from core.database import DatabaseModel
from core.help import Help
from core.utils import Hook, Plugin


class Anya(lightbulb.BotApp):
    hooks: dict[str, Hook] = {}
    __version__ = "0.0.1"

    def __init__(self, token: str) -> None:
        super().__init__(
            token,
            intents=hikari.Intents(hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.GUILD_MEMBERS),
            help_class=Help,
            help_slash_command=True,
        )

        self.load_extensions_from("plugins")
        miru.load(self)
        self.event_manager.subscribe(hikari.StartingEvent, self.setup_hook)

    async def setup_hook(self, _: typing.Any) -> None:
        self.db = await DatabaseModel().setup(self)
        [
            lightbulb.check_exempt(lambda c: c.author.id in self.owner_ids)(command)  # type: ignore
            for command in self.slash_commands.values()
        ]

    def get_me(self) -> hikari.OwnUser:
        assert (user := super().get_me()) is not None, "Self user not cached."
        return user

    @property
    def plugins(self) -> typing.MutableMapping[str, Plugin]:
        return typing.cast(typing.MutableMapping[str, Plugin], super().plugins)

    def run(self) -> None:
        super().run(
            activity=hikari.Activity(name="waku waku!", type=hikari.ActivityType.PLAYING), status=hikari.Status.IDLE
        )

    def meta_embed(self, description: str, color: hikari.Color | int = Color.ANYA) -> hikari.Embed:
        return hikari.Embed(description=description, color=color).set_footer(
            text=f"ANYA | v{self.__version__}", icon=self.get_me().display_avatar_url
        )

    @staticmethod
    def success_embed(description: str) -> hikari.Embed:
        return hikari.Embed(description=f"`{Chars.TICK}` | {description}", color=Color.GREEN)

    @staticmethod
    def fail_embed(description: str) -> hikari.Embed:
        return hikari.Embed(description=f"`{Chars.FAIL}` | {description}", color=Color.RED)

    def load_hooks(self, _loc: str, *, dir: bool = False) -> None:
        if dir is False:
            module = importlib.import_module(_loc)
            self.hooks.update({hook.name: hook for hook in module.__dict__.values() if isinstance(hook, Hook)})
            return

        for file in os.listdir(_loc):
            if file.startswith("__"):
                continue
            module = importlib.import_module(f"{_loc}.{file.strip('.py')}")
            self.hooks.update({hook.name: hook for hook in module.__dict__.values() if isinstance(hook, Hook)})
