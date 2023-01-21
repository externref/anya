from __future__ import annotations

import argparse
import ast
import asyncio
import contextlib
import datetime
import enum
import inspect
import io
import os
import typing

import attrs
import dotenv
import hikari
import lightbulb
import miru
import toolbox

from core.logging import create_logging_setup

if typing.TYPE_CHECKING:
    from core.bot import Anya

dotenv.load_dotenv()  # type: ignore


parser = argparse.ArgumentParser(prog="Anya!", usage="python -m . *args", description="Debug tools yuh")
parser.add_argument("-d", "--dev", action="store_true", help="Provide for dev mode ( will use dev token ).")


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


class Plugin(lightbulb.Plugin):
    def __init__(self, name: str, description: str, pos: int, hide: bool = False):
        self.pos = pos
        self.hidden = hide
        super().__init__(name, description)

    @property
    def bot(self) -> Anya:
        return typing.cast("Anya", super().bot)


class BaseView(miru.View):
    bound_to: int

    async def view_check(self, context: miru.ViewContext) -> bool:
        if context.author.id != self.bound_to:
            await context.respond(
                self.bot.fail_embed(f"The help session was started by <@{self.bound_to}>, only they can navigate."),
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return False
        return True

    @property
    def bot(self) -> Anya:
        return typing.cast("Anya", super().bot)


def command(
    name: str, description: str, **kwargs: typing.Any
) -> typing.Callable[[lightbulb.decorators.CommandCallbackT], lightbulb.CommandLike]:  # type: ignore
    return lightbulb.command(name, description, app_command_dm_enabled=False, **kwargs)


def format_greeting(msg: str, member: hikari.User, guild: hikari.Guild) -> str:
    return msg.format(
        **{
            "member": str(member),
            "member_name": member.username,
            "member_discriminator": member.discriminator,
            "member_id": member.id,
            "member_avatar": member.display_avatar_url.url,
            "server_name": guild.name,
            "member_creation_timestamp": toolbox.format_dt(member.created_at),
            "current_timestamp": toolbox.format_dt(datetime.datetime.utcnow().astimezone()),
            "member_count": len(guild.get_members()),
        }
    )


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


class ANSI(enum.IntEnum):
    NORMAL_FORMAT = 0
    BOLD_FORMAT = 1
    UNDERLINE_FORMAT = 4
    GRAY_TEXT = 30
    RED_TEXT = 31
    GREEN_TEXT = 32
    YELLOW_TEXT = 33
    BLUE_TEXT = 34
    PINK_TEXT = 35
    CYAN_TEXT = 36
    WHITE_TEXT = 37
    FIREFLY_DARK_BLUE_BACKGROUND = 40
    ORANGE_BACKGROUND = 41
    MARBLE_BLUE_BACKGROUND = 42
    GREYISH_TURQUOISE_BACKGROUND = 43
    GRAY_BACKGROUND = 44
    INDIGO_BACKGROUND = 45
    LIGHT_GRAY_BACKGROUND = 46
    WHITE_BACKGROUND = 0


class ANSIBuilder:
    def __init__(self) -> None:
        self.bucket: list[str] = []

    def write(self, text: str, *ansi: ANSI | int) -> ANSIBuilder:
        _ansi = ";".join(map(lambda arg: str(arg.value) if isinstance(arg, ANSI) else str(arg), ansi))
        self.bucket.append(f"\033[{_ansi}m{text}\033[0m")
        return self

    def get_str(self, *, join: str = "", codeblock: bool = False) -> str:
        return f"```ansi\n{join.join(self.bucket)}\n```" if codeblock is True else ", ".join(self.bucket)
