from __future__ import annotations

import typing

import attrs
import hikari

if typing.TYPE_CHECKING:
    from core.bot import Anya
    from kai.slash import SlashCommand


@attrs.define(kw_only=True)
class CommandHandler:

    slash_commands: dict[str, SlashCommand] = {}
    bot: Anya

    async def create_slash_command(self, name: str) -> None:
        command = self.slash_commands.get(name)
        assert command is not None, "Tried to register invalid command."
        builder = hikari.impl.SlashCommandBuilder(
            command.command_name,
            command.command_description,
        ).set_is_dm_enabled(False)
        [
            builder.add_option(hikari.CommandOption(type=data[0], name=name, description=data[1]))
            for name, data in command.options.items()
        ]
        await builder.create(self.bot.rest, self.bot.get_me().id)

    async def run_commands(self, inter: hikari.CommandInteraction) -> None:
        if (command := self.slash_commands.get(inter.command_name)) is None:
            return
        await command(inter)
