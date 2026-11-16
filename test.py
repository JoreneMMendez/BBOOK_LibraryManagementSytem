

from rich.console import Console, Group
from rich.panel import Panel
from rich.layout import Layout


console = Console()
layout = Layout()

layout.split_column(
    Layout(name="navSection", ratio=2),
    Layout(name="input", ratio=1)
)
layout["navSection"].split_row(
    Layout(Panel("",)),
    Layout(Panel("",title="Nav"))
)
layout["input"].update(Panel("",title="Input"))
console.print(layout)