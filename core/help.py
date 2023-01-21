from __future__ import annotations

import typing

import hikari
import lightbulb

from components.paginators import LazyHelpPaginator
from core.consts import ImageURLs
from core.utils import ANSI, ANSIBuilder, Plugin

if typing.TYPE_CHECKING:
    from core.bot import Anya


class Help(lightbulb.BaseHelpCommand):
    @property
    def bot(self) -> Anya:
        return typing.cast("Anya", super().bot)

    def create_plugin_help(self, plugin: Plugin) -> hikari.Embed:
        embed = (
            self.bot.meta_embed("")
            .set_author(name=f"{plugin.name.title()} Commands")
            .set_thumbnail(self.bot.get_me().display_avatar_url)
        )
        for command in plugin.all_commands:

            if isinstance(command, lightbulb.SlashCommandGroup):
                builder = ANSIBuilder().write(f"Use /help {command.name} for details about usage.", ANSI.RED_TEXT)

            elif isinstance(command, lightbulb.SlashCommand):
                builder = ANSIBuilder().write("/" + command.signature, ANSI.YELLOW_TEXT)
            else:
                builder = ANSIBuilder()
            embed.add_field("/" + command.name.lower(), f"{command.description}\n{builder.get_str(codeblock=True)}")
        return embed

    def create_bot_help(self) -> hikari.Embed:
        embed = self.bot.meta_embed("").set_image(ImageURLs.BANNER).set_author(name="Help Command")
        for p_name, plugin in self.bot.plugins.items():
            if plugin.hidden is True:
                continue
            builder = ANSIBuilder()
            for command in plugin.all_commands:
                if isinstance(command, lightbulb.SlashCommandGroup):
                    builder.write(
                        f"\033[0m, \033[{ANSI.GREEN_TEXT}m".join(
                            f"{command.name} {c.name}" for c in command.subcommands.values()
                        ),
                        ANSI.GREEN_TEXT,
                    )
                elif isinstance(command, lightbulb.SlashCommand):
                    builder.write(command.name, ANSI.BLUE_TEXT)
            print(builder.bucket)
            embed.add_field(f"{p_name.title()} Commands", builder.get_str(codeblock=True, join=", "))
        assert embed.description is not None
        return embed

    async def send_bot_help(self, context: lightbulb.SlashContext) -> None:
        comp = LazyHelpPaginator(self, home=(embed := self.create_bot_help()), bound_to=context.author.id)
        res = await context.respond(embed=embed, components=comp.build())
        await comp.start(res)

    async def send_plugin_help(self, context: lightbulb.SlashContext, plugin: Plugin) -> None:
        comp = LazyHelpPaginator(self, home=(self.create_bot_help()), bound_to=context.author.id)
        res = await context.respond(embed=self.create_plugin_help(plugin), components=comp.build())
        await comp.start(res)

    async def send_command_help(self, context: lightbulb.SlashContext, command: lightbulb.SlashCommand) -> None:
        return await super().send_command_help(context, command)

    async def send_group_help(
        self, context: lightbulb.SlashContext, group: lightbulb.SlashCommandGroup | lightbulb.SlashSubGroup
    ) -> None:
        return await super().send_group_help(context, group)
