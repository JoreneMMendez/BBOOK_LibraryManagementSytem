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


console = Console()
layout = Layout()
group = Group()

max_height = 4

def logo():
    logo_text = r""" ██████▄  ██████▄   ▄██████▄   ▄██████▄  ███   ███
███  ▐█▌ ███  ▐█▌ ███▀  ▀███ ███▀  ▀███ ███  ▄██▀
███▀▀▀█▄ ███▀▀▀█▄ ███    ███ ███    ███ ███▀▀██▄ 
███▄▄▄██ ███▄▄▄██ ▀███▄▄███▀ ▀███▄▄███▀ ███   ███
▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀    ▀▀▀▀▀▀     ▀▀▀▀▀▀   ▀▀▀   ▀▀▀ """

    logo_strip = Text(logo_text.strip("\n"), no_wrap=True, overflow="crop")
    return Align.center(Panel(
        logo_strip,
        title="Welcome to",
        subtitle="Library Management System",
        expand=False,
    ))




layout.split_column(
    Layout(" ",size=6),
    Layout(name="header", size=9),
    Layout(" ",size=1),
    Layout(name="navSec", size=4),
    Layout(name="inputSec",size=3),

)
layout["header"].update(
    Layout(Panel(logo()))
)

layout["navSec"].split_row(
    Layout(
        Panel(Align.center("[1]\n[0]"), title="Menu", title_align="left"), ratio=1),

    Layout(
        Panel("Login\nExit...", title="Selection"), ratio=4),
)
layout["inputSec"].split_row(
    Layout(
        Panel("[]: ", title="Input", title_align="left"), ratio=4),
    Layout(
        Panel("[!]"),ratio=2)
)



def menu():
    with Live(
            console=console, refresh_per_second=1, screen=False
    ) as live:
        counter = 0
        while True:
            console.clear()
            console.print(Align.center(Padding(layout, (0, 5))))

            tm.sleep(1)
            counter += 1
            if counter == 100:
                return




menu()