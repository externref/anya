from __future__ import annotations

import os
import typing

import asyncpg  # type: ignore

if typing.TYPE_CHECKING:
    from core.bot import Anya


class DatabaseModel:
    pool: asyncpg.Pool
    bot: Anya

    async def setup(self, bot: Anya) -> DatabaseModel:
        self.pool = await asyncpg.create_pool(os.environ["PGSQL_URL"])  # type: ignore
        self.bot = bot
        with open("setup_queries.sql") as config:
            [(print(query), await self.pool.execute(query)) for query in config.read().split("\n\n\n")]  # type: ignore
        return self
