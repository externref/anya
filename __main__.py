# type: ignore (Pyright doesn't like if i name the file __main__.py)

from core.bot import Anya
from core.utils import parser_and_run

parser_and_run(Anya).run()
