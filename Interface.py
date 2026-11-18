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


# all the panels are made here
def makePanel(content, title=None, padding=(0, 2), width=None):
    if title is not None:
        title = Text(title, style="accent")
    return Panel(content, title=title, title_align="left", border_style="border", box=box.ROUNDED, padding=padding, style="main", width=width)


# clear the screen and the old lines above it
def clearScreen():
    console.clear()
    if not getattr(console, "legacy_windows", False):
        print("\033[3J", end="", flush=True)


# a part of the screen with a fixed height
def section(renderable, height):
    return Layout(renderable, size=height)


# count the rows something needs
def measure(renderable):
    width = console.size.width - margin * 2 - 4
    return len(console.render_lines(renderable, console.options.update(width=width)))


# the input box at the bottom, the error shows on its border
def inputPanel(title, error=""):
    subtitle = None
    if error != "":
        subtitle = Text.from_markup(" " + error + " ")
    return Panel(
        Text(" "),
        title=Text(" " + title + " ", style="accent"),
        title_align="left",
        subtitle=subtitle,
        subtitle_align="left",
        border_style="key",
        box=box.ROUNDED,
        padding=(0, 2),
        style="main",
    )


# put the parts and the input box in one layout
def baseLayout(parts, inputTitle="Input", error=""):
    layout = Layout()
    layout.split_column(*parts, section(inputPanel(inputTitle, error), 3))
    return layout


# clear the screen and draw everything inside one big box
# center adds blank lines on top
def drawScreen(layout, center=False):
    clearScreen()
    rows = 0
    for child in layout.children:
        rows = rows + child.size
    subtitle = datetime.now().strftime("%Y-%m-%d  %H:%M")
    if session["user"] != "":
        subtitle = session["user"] + "  |  " + subtitle
    frame = Panel(
        layout,
        title=Text(" BBOOK ", style="accent"),
        title_align="left",
        subtitle=Text(" " + subtitle + " ", style="muted"),
        subtitle_align="right",
        border_style="border",
        box=box.ROUNDED,
        padding=(0, 1),
        style="main",
        height=rows + 2,
    )
    if center:
        space = (console.size.height - rows - 2) // 2
        for blank in range(min(space, max_height)):
            console.print()
    console.print(Padding(frame, (0, margin)), height=rows + 2)


# read the typing inside the input box
# move the cursor up into the box first, then back down after Enter
def readInput(password=False):
    console.control(Control.move_to_column(margin + 5, -3))
    text = console.input("[key]>[/key] ", password=password)
    console.control(Control.move(0, 2))
    return text


# print a short message under the box
def say(text):
    lead = ""
    if text.startswith("\n"):
        lead = "\n"
        text = text[1:]
    console.print(lead + " " * margin + text)


# fill a section with the menu and selection panels
# options is a list of (key, label, note)
def fillNavSection(section, options):
    width = 0
    for key, label, note in options:
        if len(label) > width:
            width = len(label)
    keys = Text(justify="center")
    labels = Text(no_wrap=True)
    for index in range(len(options)):
        key, label, note = options[index]
        keys.append("[" + key + "]", style="key")
        labels.append(label.ljust(width + 3), style="bold")
        labels.append(note, style="muted")
        if index < len(options) - 1:
            keys.append("\n")
            labels.append("\n")
    section.split_row(
        Layout(makePanel(Align.center(keys), "Menu"), ratio=1),
        Layout(makePanel(labels, "Selection"), ratio=4),
    )


# a section for the menu
def navSection(options):
    nav = Layout(size=len(options) + 2)
    fillNavSection(nav, options)
    return nav


# screen for all the sub menus
def subMenuInterface(title, options):
    return baseLayout([
        section(ascii("3", title), 1),
        section(Text(" "), 1),
        navSection(options),
    ], "Your choice")


# screen for questions and tables, shows screen["body"]
# the question is the title of the input box
def formInterface(inputTitle="Input", error=""):
    parts = [
        section(ascii("3", screen["title"]), 1),
        section(Text(" "), 1),
    ]
    if len(screen["body"]) > 0:
        body = Group(*screen["body"])
        parts.append(section(body, measure(body)))
        parts.append(section(Text(" "), 1))
    return baseLayout(parts, inputTitle, error)
