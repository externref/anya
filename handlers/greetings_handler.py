import hikari
import lightbulb


class GreetingsHandler:
    @staticmethod
    async def set_channel(
        context: lightbulb.Context,
        greeting: str,
        channel: hikari.GuildTextChannel,
    ) -> None:
        """Helper function for commands used for setting greeting channels.

        Paramaters
        ----------

            context: :class:`lightbulb.Context`
                The context which awaited this coro.
            greeting: :class:`str`
                Type of greeting.
            channel: :class:`hikari.GuildTextChannel`
                The new channel to setup for greetings.

        """
        data = await context.bot.greeting_db.get_greeting_data_for(  # type: ignore
            greeting, context.guild_id
        )
        if not data:
            await context.bot.greeting_db.set_welcome_data_for_guild(  # type: ignore
                context.guild_id, channel.id
            )
        else:
            await context.bot.greeting_db.update_channel_for(  # type: ignore
                greeting, context.guild_id, channel.id
            )

        await context.respond(
            embed=hikari.Embed(
                description=f"Set {greeting} channel to **{channel.name}** (<#{channel.id}>",
                color=context.bot.colors.peach_yellow,  # type: ignore
            ),
            reply=True,
        )

    @staticmethod
    async def set_message(
        context: lightbulb.Context, greeting: str, message: str
    ) -> None:
        """
        Updating the welcome message in the database.

        Paramaters
        ----------

            context: :class:`lightbulb.Context`
                The context which called the command.
            greeting: :class:`str`
                Type of greeting ( welcome/ goodbye )
            message: :class:`str`
                The mew message to set.

        """
        await context.bot.greeting_db.update_message_for(  # type: ignore
            greeting, context.guild_id, message
        )
        await context.respond(
            embed=hikari.Embed(
                description=message, color=context.bot.colors.green  # type: ignore
            ).set_author(name="Set welcome message to:"),
            reply=True,
        )

    @staticmethod
    async def set_welcome_bytes(
        context: lightbulb.Context, greeting: str, data_bytes: bytes
    ) -> None:
        """
        Setting up welcome/goodbye image for the guild.

        Paramaters
        ----------

            context: :class:`lightbulb.Context`
                The context which called the command.
            greeting: :class:`str`
                Type of greeting.
            data_bytes: :class:`bytes`
                Bytes of the image data.

        """

        await context.bot.greeting_db.set_image_for(  # type: ignore
            greeting, context.guild_id, data_bytes
        )
