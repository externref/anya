from __future__ import annotations

import argparse
import ast
import asyncio
import contextlib
import inspect
import io
import os
import typing

import attrs
import dotenv
import lightbulb

from core.logging import create_logging_setup

if typing.TYPE_CHECKING:
    from core.bot import Anya
dotenv.load_dotenv()  # type: ignore
parser = argparse.ArgumentParser(prog="Anya!", usage="python -m . *args", description="Debug tools yuh")
parser.add_argument("-d", "--dev", action="store_true", help="Provide for dev mode ( will use dev token ).")


class Plugin(lightbulb.Plugin):
    def __init__(self, name: str, description: str, pos: int):
        self.pos = pos
        super().__init__(name, description)

    @property
    def bot(self) -> Anya:
        return typing.cast("Anya", super().bot)


@attrs.define(kw_only=True)
class Hook:
    name: str
    callback: typing.Callable[..., typing.Any]

    def __call__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
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


class Eval:
    def add_returns(self, body: typing.Any) -> None:
        if isinstance(body[-1], ast.Expr):
            body[-1] = ast.Return(body[-1].value)
            ast.fix_missing_locations(body[-1])

        # for if statements, we insert returns into the body and the orelse
        if isinstance(body[-1], ast.If):
            self.add_returns(body[-1].body)
            self.add_returns(body[-1].orelse)

        # for with blocks, again we insert returns into the body
        if isinstance(body[-1], ast.With):
            self.add_returns(body[-1].body)

    async def f_eval(self, *, code: str, renv: dict[str, typing.Any]) -> typing.Any:
        _fn_name = "anya_eval"
        code = "\n".join(f"    {i}" for i in code.strip().splitlines())
        stdout = io.StringIO()
        stderr = io.StringIO()
        try:
            parsed: typing.Any = ast.parse(f"async def {_fn_name}():\n{code}")
            self.add_returns(parsed.body[0].body)
            exec(compile(parsed, filename="<ast>", mode="exec"), renv)
            fn = renv[_fn_name]
            with contextlib.redirect_stdout(stdout):
                with contextlib.redirect_stderr(stderr):
                    await fn()
        except Exception as e:
            return stdout.getvalue(), stderr.getvalue() + str(e)
        return stdout.getvalue(), stderr.getvalue()


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
    create_logging_setup(dev)
    return bot_cls(
        token,
    )
