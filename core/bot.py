from __future__ import annotations

import importlib
import os
import typing

import hikari

from core.utils import Hook
from kai.handler import CommandHandler

if typing.TYPE_CHECKING:
    import logging


class Anya(hikari.GatewayBot):
    hooks: dict[str, Hook] = {}

    def __init__(self, token: str, logger: logging.Logger) -> None:
        super().__init__(token)
        self.logger = logger
        self.load_hooks("commands", dir=True)
        self.command_handler = CommandHandler(bot=self)
        self.event_manager.subscribe(hikari.DMMessageCreateEvent, self._create_cmd_command)
        self.event_manager.subscribe(hikari.InteractionCreateEvent, self._process_interactions)
        self.hooks["meta"].run(self)

    def get_me(self) -> hikari.OwnUser:
        assert (user := super().get_me()) is not None, "Self user not cached."
        return user

    async def _create_cmd_command(self, event: hikari.DMMessageCreateEvent) -> None:
        if event.content and event.content.startswith("!create"):
            await self.command_handler.create_slash_command(event.content[8:])

    async def _process_interactions(self, event: hikari.InteractionCreateEvent) -> None:
        if event.interaction.type is hikari.InteractionType.APPLICATION_COMMAND:
            await self.command_handler.run_commands(typing.cast(hikari.CommandInteraction, event.interaction))

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
