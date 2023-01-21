from __future__ import annotations

import typing

import hikari
import miru

from core.consts import Emojis
from core.utils import BaseView

if typing.TYPE_CHECKING:
    from core.help import Help
    from core.utils import Plugin


class LazyHelpPaginator(BaseView):
    help_context: Help
    index: int
    plugins: dict[int, Plugin]
    home: hikari.Embed
    bound_to: int

    def __init__(self, help_context: Help, *, home: hikari.Embed, bound_to: int) -> None:
        self.help_context = help_context
        self.plugins: dict[int, Plugin] = {}
        for i, plugin in enumerate(
            sorted([p for p in help_context.bot.plugins.values() if p.hidden is False], key=lambda p: p.pos), start=1
        ):
            self.plugins[i] = plugin
        self.index = 0
        self.home = home
        self.bound_to = bound_to
        super().__init__(timeout=120)

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True

        assert self.message is not None, "view was not started properly"
        await self.message.edit(components=self.build())

    def to_page(self, page: int | None, *, or_home: bool = False) -> hikari.Embed:
        self.index = page or 0
        return (
            self.help_context.create_plugin_help(self.plugins[page])
            if isinstance(page, int) and or_home is False
            else self.home
        ).set_footer(f"Page: {self.index or 'Home'}/{len(self.plugins)}")

    def copy(self) -> LazyHelpPaginator:
        return LazyHelpPaginator(self.help_context, home=self.home, bound_to=self.bound_to)

    @miru.button(emoji=Emojis.HOME, custom_id="home", style=hikari.ButtonStyle.PRIMARY)
    async def _home(self, button: miru.Button, context: miru.ViewContext) -> None:
        await context.edit_response(embed=self.to_page(0, or_home=True))

    @miru.button(emoji=Emojis.PREVIOUS, custom_id="previous", style=hikari.ButtonStyle.PRIMARY)
    async def previous(self, button: miru.Button, context: miru.ViewContext) -> None:
        if self.index < 2:
            await context.respond(
                self.bot.fail_embed("No readable pages before this page"), flags=hikari.MessageFlag.EPHEMERAL
            )
            return
        await context.edit_response(embed=self.to_page(self.index - 1))

    @miru.button(emoji=Emojis.DUSTBIN, custom_id="bin", style=hikari.ButtonStyle.PRIMARY)
    async def disable(self, button: miru.Button, context: miru.ViewContext) -> None:
        await context.defer()
        await self.on_timeout()

    @miru.button(emoji=Emojis.NEXT, custom_id="next", style=hikari.ButtonStyle.PRIMARY)
    async def next(self, button: miru.Button, context: miru.ViewContext) -> None:
        if self.index == len(self.plugins):
            await context.respond(
                self.bot.fail_embed("No readable pages after this page"), flags=hikari.MessageFlag.EPHEMERAL
            )
            return
        await context.edit_response(embed=self.to_page(self.index + 1))
