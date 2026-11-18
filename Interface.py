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


# small loading bar
def loadingBar(message):
    clearScreen()
    for blank in range(6):
        console.print()
    with Live(console=console, refresh_per_second=20) as live:
        for step in range(21):
            text = Text(justify="center")
            text.append(message + "\n\n", style="bold")
            text.append("█" * step, style="accent")
            text.append("░" * (20 - step), style="muted")
            live.update(Align.center(makePanel(text, width=44)))
            tm.sleep(0.03)


# add (Admin only) to the label for staff
def adminLabel(text, currentUser):
    if currentUser.isAdmin():
        return text
    return text + " (Admin only)"


def menuInterface():
    return baseLayout([
        section(ascii("1"), 6),
        section(Text(" "), 1),
        navSection([
            ("1", "Login", "Sign in to the system"),
            ("0", "Exit...", "Close the program"),
        ]),
    ], "Your choice")



def loginInterface(message="", inputTitle="Username"):
    text = Text(justify="center")
    text.append("Sign in to continue\n", style="accent")
    text.append("Type 0 as the username to go back\n", style="muted")
    text.append_text(Text.from_markup(message + " "))
    return baseLayout([
        section(ascii("1"), 6),
        section(Text(" "), 1),
        section(text, 3),
    ], inputTitle)



def registerInterface():
    startScreen("User Management  >  Register a user")
    addNote("[muted]Type 0 at the username to cancel.[/muted]")
    return formInterface("Username")


# a small card for the dashboard
def statCard(number, label, numberStyle="accent"):
    text = Text(justify="center")
    text.append(number + "\n", style=numberStyle)
    text.append(label, style="muted")
    return Layout(makePanel(text), ratio=1)



def DashboardInterface(currentUser):
    summary = reports.getSummary()
    now = datetime.now()

    options = [
        ("1", "Books", "View, add, update and delete books"),
        ("2", "Borrowers", "Manage the library members"),
        ("3", "Borrow / Return", "Lend books, take them back, history"),
        ("4", "Search", "Find books, borrowers and records"),
        ("5", "Reports", "Overdue, most borrowed, categories"),
        ("6", adminLabel("User Management", currentUser), "Accounts, roles and passwords"),
        ("7", "System Settings", "Change the theme or your password"),
        ("0", "Logout", "Sign out of your account"),
    ]

    # status bar: user, date and time
    status = Table.grid(expand=True)
    status.add_column(justify="left")
    status.add_column(justify="center")
    status.add_column(justify="right")
    status.add_row(
        Text.assemble(("", "accent"), (currentUser.getUsername(), "bold"), ("   " + currentUser.getRole(), "muted")),
        Text(now.strftime("%A, %Y-%m-%d"), style="main"),
        Text(now.strftime("%H:%M:%S"), style="accent"),
    )

    if summary["overdue"] > 0:
        overdueStyle = "bad"
    else:
        overdueStyle = "good"

    stats = Layout(size=4)
    stats.split_row(
        statCard(str(summary["titles"]), "Book titles"),
        statCard(str(summary["available"]) + " / " + str(summary["copies"]), "Copies available"),
        statCard(str(summary["borrowed"]), "Currently borrowed"),
        statCard(str(summary["borrowers"]), "Borrowers"),
        statCard(str(summary["overdue"]), "Overdue", overdueStyle),
    )

    return baseLayout([
        section(ascii("1"), 6),
        section(Text(" "), 1),
        section(status, 1),
        section(Text(" "), 1),
        stats,
        section(Text(" "), 1),
        navSection(options),
    ], "Your choice")


# a small card for the dashboard
def statCard(number, label, numberStyle="accent"):
    text = Text(justify="center")
    text.append(number + "\n", style=numberStyle)
    text.append(label, style="muted")
    return Layout(makePanel(text), ratio=1)



def DashboardInterface(currentUser):
    summary = reports.getSummary()
    now = datetime.now()

    options = [
        ("1", "Books", "View, add, update and delete books"),
        ("2", "Borrowers", "Manage the library members"),
        ("3", "Borrow / Return", "Lend books, take them back, history"),
        ("4", "Search", "Find books, borrowers and records"),
        ("5", "Reports", "Overdue, most borrowed, categories"),
        ("6", adminLabel("User Management", currentUser), "Accounts, roles and passwords"),
        ("7", "System Settings", "Change the theme or your password"),
        ("0", "Logout", "Sign out of your account"),
    ]

    # status bar: user, date and time
    status = Table.grid(expand=True)
    status.add_column(justify="left")
    status.add_column(justify="center")
    status.add_column(justify="right")
    status.add_row(
        Text.assemble(("", "accent"), (currentUser.getUsername(), "bold"), ("   " + currentUser.getRole(), "muted")),
        Text(now.strftime("%A, %Y-%m-%d"), style="main"),
        Text(now.strftime("%H:%M:%S"), style="accent"),
    )

    if summary["overdue"] > 0:
        overdueStyle = "bad"
    else:
        overdueStyle = "good"

    stats = Layout(size=4)
    stats.split_row(
        statCard(str(summary["titles"]), "Book titles"),
        statCard(str(summary["available"]) + " / " + str(summary["copies"]), "Copies available"),
        statCard(str(summary["borrowed"]), "Currently borrowed"),
        statCard(str(summary["borrowers"]), "Borrowers"),
        statCard(str(summary["overdue"]), "Overdue", overdueStyle),
    )

    return baseLayout([
        section(ascii("1"), 6),
        section(Text(" "), 1),
        section(status, 1),
        section(Text(" "), 1),
        stats,
        section(Text(" "), 1),
        navSection(options),
    ], "Your choice")


# a small card for the dashboard
def statCard(number, label, numberStyle="accent"):
    text = Text(justify="center")
    text.append(number + "\n", style=numberStyle)
    text.append(label, style="muted")
    return Layout(makePanel(text), ratio=1)



def DashboardInterface(currentUser):
    summary = reports.getSummary()
    now = datetime.now()

    options = [
        ("1", "Books", "View, add, update and delete books"),
        ("2", "Borrowers", "Manage the library members"),
        ("3", "Borrow / Return", "Lend books, take them back, history"),
        ("4", "Search", "Find books, borrowers and records"),
        ("5", "Reports", "Overdue, most borrowed, categories"),
        ("6", adminLabel("User Management", currentUser), "Accounts, roles and passwords"),
        ("7", "System Settings", "Change the theme or your password"),
        ("0", "Logout", "Sign out of your account"),
    ]

    # status bar: user, date and time
    status = Table.grid(expand=True)
    status.add_column(justify="left")
    status.add_column(justify="center")
    status.add_column(justify="right")
    status.add_row(
        Text.assemble(("", "accent"), (currentUser.getUsername(), "bold"), ("   " + currentUser.getRole(), "muted")),
        Text(now.strftime("%A, %Y-%m-%d"), style="main"),
        Text(now.strftime("%H:%M:%S"), style="accent"),
    )

    if summary["overdue"] > 0:
        overdueStyle = "bad"
    else:
        overdueStyle = "good"

    stats = Layout(size=4)
    stats.split_row(
        statCard(str(summary["titles"]), "Book titles"),
        statCard(str(summary["available"]) + " / " + str(summary["copies"]), "Copies available"),
        statCard(str(summary["borrowed"]), "Currently borrowed"),
        statCard(str(summary["borrowers"]), "Borrowers"),
        statCard(str(summary["overdue"]), "Overdue", overdueStyle),
    )

    return baseLayout([
        section(ascii("1"), 6),
        section(Text(" "), 1),
        section(status, 1),
        section(Text(" "), 1),
        stats,
        section(Text(" "), 1),
        navSection(options),
    ], "Your choice")


# a small card for the dashboard
def statCard(number, label, numberStyle="accent"):
    text = Text(justify="center")
    text.append(number + "\n", style=numberStyle)
    text.append(label, style="muted")
    return Layout(makePanel(text), ratio=1)



def DashboardInterface(currentUser):
    summary = reports.getSummary()
    now = datetime.now()

    options = [
        ("1", "Books", "View, add, update and delete books"),
        ("2", "Borrowers", "Manage the library members"),
        ("3", "Borrow / Return", "Lend books, take them back, history"),
        ("4", "Search", "Find books, borrowers and records"),
        ("5", "Reports", "Overdue, most borrowed, categories"),
        ("6", adminLabel("User Management", currentUser), "Accounts, roles and passwords"),
        ("7", "System Settings", "Change the theme or your password"),
        ("0", "Logout", "Sign out of your account"),
    ]

    # status bar: user, date and time
    status = Table.grid(expand=True)
    status.add_column(justify="left")
    status.add_column(justify="center")
    status.add_column(justify="right")
    status.add_row(
        Text.assemble(("", "accent"), (currentUser.getUsername(), "bold"), ("   " + currentUser.getRole(), "muted")),
        Text(now.strftime("%A, %Y-%m-%d"), style="main"),
        Text(now.strftime("%H:%M:%S"), style="accent"),
    )

    if summary["overdue"] > 0:
        overdueStyle = "bad"
    else:
        overdueStyle = "good"

    stats = Layout(size=4)
    stats.split_row(
        statCard(str(summary["titles"]), "Book titles"),
        statCard(str(summary["available"]) + " / " + str(summary["copies"]), "Copies available"),
        statCard(str(summary["borrowed"]), "Currently borrowed"),
        statCard(str(summary["borrowers"]), "Borrowers"),
        statCard(str(summary["overdue"]), "Overdue", overdueStyle),
    )

    return baseLayout([
        section(ascii("1"), 6),
        section(Text(" "), 1),
        section(status, 1),
        section(Text(" "), 1),
        stats,
        section(Text(" "), 1),
        navSection(options),
    ], "Your choice")


def bookInterface(currentUser):
    return subMenuInterface("Books", [
        ("1", "View all books", "List every book and its copies"),
        ("2", "Add a book", "Register a new title"),
        ("3", "Update a book", "Edit title, author, category, copies"),
        ("4", adminLabel("Delete a book", currentUser), "Remove a book from the library"),
        ("0", "Back", "Return to the main menu"),
    ])


def borrowerInterface(currentUser):
    return subMenuInterface("Borrowers", [
        ("1", "View all borrowers", "List every member"),
        ("2", "Add a borrower", "Register a new member"),
        ("3", "Update a borrower", "Edit name or contact"),
        ("4", adminLabel("Delete a borrower", currentUser), "Remove a member"),
        ("0", "Back", "Return to the main menu"),
    ])


def borrowInterface(currentUser):
    return subMenuInterface("Borrow / Return", [
        ("1", "Borrow a book", "Lend a book to a borrower"),
        ("2", "Return a book", "Take a borrowed book back"),
        ("3", "Borrowing history", "See every record"),
        ("4", "Extend a due date", "Give a borrower more days"),
        ("5", adminLabel("Delete a history record", currentUser), "Remove a returned record"),
        ("0", "Back", "Return to the main menu"),
    ])


def searchInterface():
    return subMenuInterface("Search", [
        ("1", "Search books", "Title, author, category or ID"),
        ("2", "Search borrowers", "Name, ID or contact"),
        ("3", "Search borrowing records", "Status, book or borrower"),
        ("0", "Back", "Return to the main menu"),
    ])


def reportInterface():
    return subMenuInterface("Reports", [
        ("1", "Borrowed / overdue books", "Who has what, and what is late"),
        ("2", "Most borrowed books", "The top 10 books"),
        ("3", "Books by category", "Titles, copies and loans per category"),
        ("4", "Borrower activity", "How active each borrower is"),
        ("0", "Back", "Return to the main menu"),
    ])


def userInterface():
    return subMenuInterface("User Management", [
        ("1", "View users", "List all accounts"),
        ("2", "Register a user", "Create an account"),
        ("3", "Change a user role", "Administrator or Staff"),
        ("4", "Reset a user password", "Set a new password"),
        ("5", "Delete a user", "Remove an account"),
        ("0", "Back", "Return to the main menu"),
    ])


def settingsInterface():
    return subMenuInterface("System Settings", [
        ("1", "Change terminal theme", "Pick the colors of the program"),
        ("2", "Update my password", "Needs your current password"),
        ("0", "Back to main menu", "Return to the main menu"),
    ])
