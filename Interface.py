from rich import box
from rich.align import Align
from rich.layout import Layout
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()
layout = Layout()

def logo():
    logo_text = Align.center(""" ███████████  ███████████     ███████       ███████    █████   ████
▒▒███▒▒▒▒▒███▒▒███▒▒▒▒▒███  ███▒▒▒▒▒███   ███▒▒▒▒▒███ ▒▒███   ███▒ 
 ▒███    ▒███ ▒███    ▒███ ███     ▒▒███ ███     ▒▒███ ▒███  ███   
 ▒██████████  ▒██████████ ▒███      ▒███▒███      ▒███ ▒███████    
 ▒███▒▒▒▒▒███ ▒███▒▒▒▒▒███▒███      ▒███▒███      ▒███ ▒███▒▒███   
 ▒███    ▒███ ▒███    ▒███▒▒███     ███ ▒▒███     ███  ▒███ ▒▒███  
 ███████████  ███████████  ▒▒▒███████▒   ▒▒▒███████▒   █████ ▒▒████
▒▒▒▒▒▒▒▒▒▒▒  ▒▒▒▒▒▒▒▒▒▒▒     ▒▒▒▒▒▒▒       ▒▒▒▒▒▒▒    ▒▒▒▒▒   ▒▒▒▒ """)
    console.print(Panel(logo_text, title="Welcome to", subtitle="Library Management System", box=box.ROUNDED))


layout.split_column(
    Layout(name="header", size=3),
    Layout(name="main", size=3),
    Layout(name="footer", size=3)
)
layout["header"].update(Panel(Align.center("[bold]██████████████████████  MENU  ██████████████████████[/bold]")))
layout["main"].update(Panel("",title="Navigation"))


def menu():
    while True:
        logo()
        console.print(layout)
        choice = console.print(Panel(Prompt.ask("[bold]Input[/bold]")))

        if choice == "1":
            break
        else:
            break

        return



menu()