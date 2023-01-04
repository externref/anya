from __future__ import annotations

import typing

import hikari
import miru

if typing.TYPE_CHECKING:
    from core.bot import Anya


class GreetingMessageModal(miru.Modal):
    message: str

    def __init__(self, _type: typing.Literal["welcome", "goodbye"]) -> None:
        self.type = _type
        super().__init__("Greeting Message.", timeout=3000)
        self.add_item(
            miru.TextInput(
                label=f"{_type.title()} message: ",
                style=hikari.TextInputStyle.PARAGRAPH,
                max_length=2000,
                min_length=10,
            )
        )

    async def callback(self, context: miru.ModalContext) -> None:
        bot = typing.cast("Anya", context.bot)
        await bot.db.pool.execute(f"UPDATE greetings SET {self.type}_message = $1", list(context.values.values())[0])  # type: ignore
        print(list(context.values.values())[0])
        await context.respond(embed=bot.success_embed("The message was updated!"), flags=hikari.MessageFlag.EPHEMERAL)
