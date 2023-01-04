import typing

import hikari
import miru

from components.modals import GreetingMessageModal


class GreetingMessageView(miru.View):
    def __init__(self, _type: typing.Literal["welcome", "goodbye"]) -> None:
        self.type: typing.Literal["welcome", "goodbye"] = _type
        super().__init__()

    @miru.button(label="Setup Message", style=hikari.ButtonStyle.SECONDARY)
    async def setup(self, _: miru.Button, context: miru.ViewContext) -> None:
        await context.respond_with_modal(GreetingMessageModal(self.type))
