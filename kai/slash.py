from __future__ import annotations

import importlib
import typing

import attrs
import hikari

if typing.TYPE_CHECKING:
    from core.bot import Anya

    SlashCommandCallbackT: typing.TypeAlias = typing.Callable[
        [Anya, hikari.CommandInteraction], typing.Awaitable[typing.Any]
    ]


@attrs.define(kw_only=True)
class SlashCommand:
    bot: Anya = attrs.field(init=False)
    command_name: str
    command_description: str
    options: dict[str, tuple[hikari.OptionType, str]] = {}
    callback: SlashCommandCallbackT

    def __call__(self, inter: hikari.CommandInteraction) -> typing.Awaitable[typing.Any]:
        return self.callback(self.bot, inter)

    def load_to(self, bot: Anya) -> None:
        bot.command_handler.slash_commands[self.command_name] = self
        self.bot = bot

    @classmethod
    def init(
        cls, name: str, description: str, options: dict[str, tuple[hikari.OptionType, str]] = {}
    ) -> typing.Callable[[SlashCommandCallbackT], SlashCommand]:
        def decorator(callback: SlashCommandCallbackT) -> SlashCommand:
            return SlashCommand(command_name=name, options=options, command_description=description, callback=callback)

        return decorator

    @staticmethod
    def in_file(path: str) -> list[SlashCommand]:
        module = importlib.import_module(path)
        return [obj for obj in module.__dict__.values() if isinstance(obj, SlashCommand)]
