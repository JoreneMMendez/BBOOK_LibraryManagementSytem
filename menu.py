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

console = Console()


layout = Layout()


class Interface:
    def __init__(self, theme: str, hasAscci: bool):
        self.theme = theme
        self.hasAscci = hasAscci

    @property
    def theme(self) -> str:
        return self._theme

    @theme.setter
    def theme(self, value: str):
        self._theme = value.lower()

    @property
    def hasAscci(self) -> bool:
        return self._hasAscci

    @hasAscci.setter
    def hasAscci(self, value: bool):
        self._hasAscci = bool(value)

    def ascii(self, designSection: str):
        logo_text = f"""[{self.theme}] 
    ██████▄  ██████▄   ▄██████▄   ▄██████▄  ███   ███
    ███  ▐█▌ ███  ▐█▌ ███▀  ▀███ ███▀  ▀███ ███  ▄██▀
    ███▀▀▀█▄ ███▀▀▀█▄ ███    ███ ███    ███ ███▀▀██▄ 
    ███▄▄▄██ ███▄▄▄██ ▀███▄▄███▀ ▀███▄▄███▀ ███   ███
    ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀    ▀▀▀▀▀▀     ▀▀▀▀▀▀   ▀▀▀   ▀▀▀ [/{self.theme}]"""

        arrow = r"""   ████
       ████
       ████
    ██████████
     ████████
      ██████
       ████
        ██"""

        if designSection == "1":
            items = []

            logo_strip = Text.from_markup(logo_text.strip("\n"))
            logo_strip.no_wrap = True
            logo_strip.overflow = "crop"
            return Align.center(
                Panel(
                    logo_strip,
                    title="Welcome to",
                    subtitle="Library Management System",
                    border_style=self.theme,
                    expand=False,
                )
            )
        elif designSection == "2":
            arrow_strip = Text(arrow.strip("\n"), no_wrap=True, overflow="crop")
            return Align.center(
                Panel(arrow_strip, border_style=self.theme, expand=False)
            )

    def UI(self):
        layout = Layout()

        if self.hasAscci:
            items.append(self.ascii("1"))
        inter = Panel(
            Group(*i)
        )

        console.print(inter)


ui = Interface("cyan", True)
ui.UI()





"""
def menuInterface():
    layout = Layout()
    layout.split_column(
        Layout(" ", size=max_height),
        Layout(name="header", size=9),

        Layout(name="navSec", size=4),
    )
    layout["header"].split_column(
        Panel(ascii("1")),
        Align.center(Panel(f"[{theme}]▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀MAIN MENU▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀[/{theme}]"), size=9)
    )

    layout["navSec"].split_row(
        Layout(
            Panel(Align.center("[1]\n[0]"), title="Menu", title_align="left"), ratio=1),

        Layout(
            Panel("Login\nExit...", title="Selection"), ratio=4),
    )

    return layout

"""