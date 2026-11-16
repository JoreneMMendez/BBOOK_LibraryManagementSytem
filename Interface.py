from time import sleep

from rich import box
from rich.padding import Padding
from rich.align import Align
from rich.layout import Layout
from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.prompt import Prompt

import time as tm


class user:
    def __init__(self, name, password):
        self._username = name
        self._userpassword = password

    def getAccount(self):
        return self._username, self._userpassword


class Dashboard:
    def __init__(self, ):
        self.Bookname

console = Console()
layout = Layout()
group = Group()

max_height = 12

#Ascii design function
def ascii(designSection = ""):
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
        logo_strip = Text(logo_text.strip("\n"), no_wrap=True, overflow="crop")
        return Align.center(
            Panel(
            logo_strip,
            title="Welcome to",
            subtitle="Library Management System",
            expand=False,)
        )
    elif designSection == "2":
        arrow_strip = Text(arrow.strip("\n"), no_wrap=True, overflow="crop")
        return Align.center(Panel(arrow_strip, expand=False))


def menuInterface():
    layout = Layout()
    layout.split_column(
        Layout(" ", size=max_height),
        Layout(name="header", size=9),
        Layout("", size=max_height - 2),
        Layout(name="navSec", size=4),
    )
    layout["header"].update(
        Panel(ascii("1"))
    )
    layout["navSec"].split_row(
        Layout(
            Panel(Align.center("[1]\n[0]"), title="Menu", title_align="left"), ratio=1),

        Layout(
            Panel("Login\nExit...", title="Selection"), ratio=4),
    )

    return layout

def loginInterface():
    layout = Layout()
    layout.split_column(
        Layout(" ", size=max_height),
        Layout(name="header", size=9),
        Layout(name="UserLogs", size=4),
    )
    layout["header"].update(
        Panel(ascii("2"))
    )
    return layout



def registerInterface():
    layout = Layout()
    layout.split_column()

    return


def DashboardInterface():
    return




def main():
    counter = 0
    while True:
        choices = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

        console.print(Padding(menuInterface(), (0, 10)))
        choice = console.input("[bold]Input: [/bold]")

        match choice:
            case "1":
                print("jkdsj")
                console.print(loginInterface())
                break
            case "2":

                break
            case _:
                console.print("Invalid choice...")
                tm.sleep(0.5)



main()