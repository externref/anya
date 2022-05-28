import os

from core.bot import Bot

if __name__ == "__main__":
    bot = Bot()
    bot.__version__ = "0.0.1"
    bot.hikari_version = __import__("hikari").__version__
    bot.lightbulb_version = __import__("lightbulb").__version__
    if os.name != "nt":
        import uvloop

        uvloop.install()
