from rich import box
from rich.padding import Padding
from rich.align import Align
from rich.layout import Layout
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt

console = Console()
layout = Layout()

max_height = 10

def logo():
    logo_text = r""" ██████▄  ██████▄   ▄██████▄   ▄██████▄  ███   ███
███  ▐█▌ ███  ▐█▌ ███▀  ▀███ ███▀  ▀███ ███  ▄██▀
███▀▀▀█▄ ███▀▀▀█▄ ███    ███ ███    ███ ███▀▀██▄ 
███▄▄▄██ ███▄▄▄██ ▀███▄▄███▀ ▀███▄▄███▀ ███   ███
▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀    ▀▀▀▀▀▀     ▀▀▀▀▀▀   ▀▀▀   ▀▀▀ """

    logo_strip = Text(logo_text.strip("\n"), no_wrap=True, overflow="crop")
    logo_panel = Panel(
        logo_strip,
        title="Welcome to",
        subtitle="Library Management System",
        expand=False,
    )
    centered = Align.center(logo_panel)
    console.print(centered)


grid = Table.grid(padding=(0, -0))
grid.add_column(width=5)   # Menu
grid.add_column(width=20)   # Navigation
grid.add_row(
    Panel("", title="Menu", height=max_height),
    Panel("", title="Navigation", height=max_height),
)




def menu():
    while True:
        console.clear()
        logo()
        console.print(Align.center(grid))
        return



menu()