from __future__ import annotations

import typing

import hikari
import miru

from core.consts import Color

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


class ConfessionModal(miru.Modal):
    confession = miru.TextInput(label="confession to send", style=hikari.TextInputStyle.PARAGRAPH)

    async def callback(self, context: miru.ModalContext) -> None:
        await context.defer()
        bot = typing.cast("Anya", context.bot)
        channel: int = await bot.db.pool.fetchval(  # type: ignore
            "SELECT channel_id FROM confession_configs WHERE guild_id = $1 ", context.guild_id
        )
        confession_id: int = (
            await bot.db.pool.fetchval("SELECT COUNT(*) FROM confession_logs WHERE guild_id = $1", context.guild_id)  # type: ignore
        ) + 1
        msg = await bot.rest.create_message(
            channel,
            embed=hikari.Embed(
                title=f"Anonymous confession | #{confession_id}", description=self.confession.value, color=Color.ANYA
            ),
        )

        await bot.db.pool.execute(  # type: ignore
            "INSERT INTO confession_logs VALUES ( $1, $2, $3, $4 )",
            context.guild_id,
            confession_id,
            context.author.id,
            msg.id,
        )
        await context.respond("Your confession was sent.", flags=hikari.MessageFlag.EPHEMERAL)
