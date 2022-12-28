from __future__ import annotations

import argparse
import asyncio
import inspect
import os
import typing

import attrs

from core.logging import create_logging_setup

if typing.TYPE_CHECKING:
    from core.bot import Anya

parser = argparse.ArgumentParser(prog="Anya!", usage="python -m . *args", description="Debug tools yuh")
parser.add_argument("-d", "--dev", action="store_true", help="Provide for dev mode ( will use dev token ).")


@attrs.define(kw_only=True)
class Hook:
    name: str
    callback: typing.Callable[..., typing.Any]

    def run(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        call = self.callback(*args, **kwargs)
        if inspect.iscoroutine(call) is True:
            asyncio.create_task(call)

    @classmethod
    def create(cls, name: str | None = None) -> typing.Callable[[typing.Callable[..., typing.Any]], Hook]:
        def decorator(callback: typing.Callable[..., typing.Any]) -> Hook:
            return cls(name=name or callback.__name__, callback=callback)

        return decorator

    def add_to_bot(self, bot: Anya) -> None:
        bot.hooks[self.name] = self


def parser_and_run(bot_cls: type[Anya]) -> Anya:
    args = parser.parse_args()
    dev: bool = False
    if args.dev:
        dev = True
        token = os.getenv("DEV_TOKEN")
        assert token is not None, "No dev token value set."
    else:
        token = os.getenv("TOKEN")
    assert token is not None, "No token value set."
    return bot_cls(token, create_logging_setup(dev))
