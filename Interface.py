import time as tm
from datetime import datetime

from rich import box
from rich.padding import Padding
from rich.align import Align
from rich.layout import Layout
from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule
from rich.live import Live
from rich.control import Control
from rich.markup import escape

import themes

console = Console()
themes.applyTheme(console, themes.default_theme)

max_height = 4  # max blank lines on top
max_attempts = 3  # login tries
margin = 10  # space on the left and right


session = {"user": ""}  # who is logged in


# what is shown on the current screen
screen = {"title": "", "body": []}


# keeps the name and role of the logged in user
class user:

    def __init__(self, name, role):
        self._username = name
        self._userrole = role

    def getUsername(self):
        return self._username

    def getRole(self):
        return self._userrole

    def isAdmin(self):
        return self._userrole == "Administrator"


# draws the logo (1), the arrow (2) or a heading line (3)
def ascii(designSection = "", label = ""):
    logo_text = r""" ██████▄  ██████▄   ▄██████▄   ▄██████▄  ███   ███
███  ▐█▌ ███  ▐█▌ ███▀  ▀███ ███▀  ▀███ ███  ▄██▀
███▀▀▀█▄ ███▀▀▀█▄ ███    ███ ███    ███ ███▀▀██▄ 
███▄▄▄██ ███▄▄▄██ ▀███▄▄███▀ ▀███▄▄███▀ ███   ███
▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀    ▀▀▀▀▀▀     ▀▀▀▀▀▀   ▀▀▀   ▀▀▀ """
    arrow = r"""   ████
   ████
   ████
██████████
 ████████
  ██████
   ████
    ██
    """
    if designSection == "1":
        lines = logo_text.strip("\n").split("\n")
        width = 0
        for line in lines:
            if len(line) > width:
                width = len(line)
        # colors of the logo lines, top to bottom
        colors = ["logo1", "logo1", "logo2", "logo3", "logo3"]
        logo_strip = Text(no_wrap=True, overflow="crop")
        for index in range(len(lines)):
            logo_strip.append(lines[index].ljust(width) + "\n", style=colors[min(index, 4)])
        logo_strip.append("L I B R A R Y   M A N A G E M E N T   S Y S T E M".center(width), style="muted")
        return Align.center(logo_strip)
    elif designSection == "2":
        arrow_strip = Text(arrow.strip("\n"), no_wrap=True, overflow="crop", style="accent")
        return Align.center(Panel(arrow_strip, expand=False, border_style="border"))
    elif designSection == "3":
        return Rule(Text(label, style="accent"), style="border", align="left")
    return Align.center(Text(" "))
