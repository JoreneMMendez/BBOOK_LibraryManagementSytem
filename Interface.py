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
