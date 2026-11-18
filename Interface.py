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

import auth
import auth
import auth
import dataManager
import dataManager
import reports
import reports
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


# start a new screen
def startScreen(title):
    screen["title"] = title
    screen["body"] = []


# add something to the screen
def addToScreen(renderable):
    screen["body"].append(renderable)


# add a line of text
def addNote(text):
    screen["body"].append(Text.from_markup(text))


# add a centered table and a blank line
def addTable(table):
    screen["body"].append(Align.center(table))
    screen["body"].append(Text(" "))


# show the question and return the answer
def ask(prompt, password=False, error=""):
    drawScreen(formInterface(prompt, error))
    return readInput(password)


# keep the answer on the screen
def remember(prompt, answer):
    screen["body"].append(Text.assemble(("> ", "key"), (prompt + ": ", "muted"), (answer, "main")))


# message for a wrong choice
def invalidChoice():
    say("[bad]Error: Invalid choice...[/bad]")
    tm.sleep(0.5)


# wait for Enter
def pause():
    ask("Press Enter to continue")


# ask for text, 0 cancels (None), Enter uses the default
def askText(prompt, default=None):
    error = ""
    while True:
        text = ask(prompt, error=error).strip()
        if text == "0":
            return None
        text = dataManager.cleanText(text)
        if text == "" and default is not None:
            text = default
        if text == "":
            error = "[bad]Error: This cannot be empty.[/bad]"
            continue
        remember(prompt, text)
        return text


# ask for a number from minValue to maxValue, 0 cancels (None)
def askNumber(prompt, minValue, maxValue, default=None):
    error = ""
    while True:
        text = ask(prompt, error=error).strip()
        if text == "0":
            return None
        if text == "" and default is not None:
            remember(prompt, str(default))
            return default
        try:
            number = int(text)
        except ValueError:
            error = "[bad]Error: Please enter a whole number.[/bad]"
            continue
        if number < minValue or number > maxValue:
            error = "[bad]Error: Enter a number from " + str(minValue) + " to " + str(maxValue) + ".[/bad]"
            continue
        remember(prompt, str(number))
        return number


# ask for a password
def askPassword(prompt):
    text = ask(prompt, password=True)
    remember(prompt, "*" * len(text))
    return text


# ask yes or no
def askYesNo(question):
    error = ""
    while True:
        answer = ask(question + " (y/n)", error=error).strip().lower()
        if answer == "y":
            remember(question, "yes")
            return True
        if answer == "n":
            remember(question, "no")
            return False
        error = "[bad]Error: Please type y or n.[/bad]"


# ask for a role, None if cancelled
def askRole():
    error = ""
    while True:
        choice = ask("Role: 1 = " + auth.ROLES[0] + ", 2 = " + auth.ROLES[1] + " (0 = cancel)", error=error)
        if choice == "1":
            remember("Role", auth.ROLES[0])
            return auth.ROLES[0]
        elif choice == "2":
            remember("Role", auth.ROLES[1])
            return auth.ROLES[1]
        elif choice == "0":
            return None
        else:
            error = "[bad]Error: Enter 1 or 2 (0 = cancel).[/bad]"


# show the result message and wait
def showResult(ok, message):
    addNote(" ")
    if ok:
        addToScreen(Text.assemble(("", "good"), (message, "good")))
    else:
        addToScreen(Text.assemble(("Error: ", "bad"), (message, "bad")))
    pause()


# only admins can continue
def requireAdmin(currentUser):
    if currentUser.isAdmin():
        return True
    startScreen("Access denied")
    addNote("[bad]Error: Access denied. Administrator only.[/bad]")
    pause()
    return False


# show a table and wait
def showTableScreen(title, table):
    startScreen(title)
    addTable(table)
    pause()


# start a new screen
def startScreen(title):
    screen["title"] = title
    screen["body"] = []


# add something to the screen
def addToScreen(renderable):
    screen["body"].append(renderable)


# add a line of text
def addNote(text):
    screen["body"].append(Text.from_markup(text))


# add a centered table and a blank line
def addTable(table):
    screen["body"].append(Align.center(table))
    screen["body"].append(Text(" "))


# show the question and return the answer
def ask(prompt, password=False, error=""):
    drawScreen(formInterface(prompt, error))
    return readInput(password)


# keep the answer on the screen
def remember(prompt, answer):
    screen["body"].append(Text.assemble(("> ", "key"), (prompt + ": ", "muted"), (answer, "main")))


# message for a wrong choice
def invalidChoice():
    say("[bad]Error: Invalid choice...[/bad]")
    tm.sleep(0.5)


# wait for Enter
def pause():
    ask("Press Enter to continue")


# ask for text, 0 cancels (None), Enter uses the default
def askText(prompt, default=None):
    error = ""
    while True:
        text = ask(prompt, error=error).strip()
        if text == "0":
            return None
        text = dataManager.cleanText(text)
        if text == "" and default is not None:
            text = default
        if text == "":
            error = "[bad]Error: This cannot be empty.[/bad]"
            continue
        remember(prompt, text)
        return text


# ask for a number from minValue to maxValue, 0 cancels (None)
def askNumber(prompt, minValue, maxValue, default=None):
    error = ""
    while True:
        text = ask(prompt, error=error).strip()
        if text == "0":
            return None
        if text == "" and default is not None:
            remember(prompt, str(default))
            return default
        try:
            number = int(text)
        except ValueError:
            error = "[bad]Error: Please enter a whole number.[/bad]"
            continue
        if number < minValue or number > maxValue:
            error = "[bad]Error: Enter a number from " + str(minValue) + " to " + str(maxValue) + ".[/bad]"
            continue
        remember(prompt, str(number))
        return number


# ask for a password
def askPassword(prompt):
    text = ask(prompt, password=True)
    remember(prompt, "*" * len(text))
    return text


# ask yes or no
def askYesNo(question):
    error = ""
    while True:
        answer = ask(question + " (y/n)", error=error).strip().lower()
        if answer == "y":
            remember(question, "yes")
            return True
        if answer == "n":
            remember(question, "no")
            return False
        error = "[bad]Error: Please type y or n.[/bad]"


# ask for a role, None if cancelled
def askRole():
    error = ""
    while True:
        choice = ask("Role: 1 = " + auth.ROLES[0] + ", 2 = " + auth.ROLES[1] + " (0 = cancel)", error=error)
        if choice == "1":
            remember("Role", auth.ROLES[0])
            return auth.ROLES[0]
        elif choice == "2":
            remember("Role", auth.ROLES[1])
            return auth.ROLES[1]
        elif choice == "0":
            return None
        else:
            error = "[bad]Error: Enter 1 or 2 (0 = cancel).[/bad]"


# show the result message and wait
def showResult(ok, message):
    addNote(" ")
    if ok:
        addToScreen(Text.assemble(("", "good"), (message, "good")))
    else:
        addToScreen(Text.assemble(("Error: ", "bad"), (message, "bad")))
    pause()


# only admins can continue
def requireAdmin(currentUser):
    if currentUser.isAdmin():
        return True
    startScreen("Access denied")
    addNote("[bad]Error: Access denied. Administrator only.[/bad]")
    pause()
    return False


# show a table and wait
def showTableScreen(title, table):
    startScreen(title)
    addTable(table)
    pause()


# ask for the login, returns a user or None
def loginFlow():
    message = ""
    for attempt in range(max_attempts):
        drawScreen(loginInterface(message, "Username"), True)
        username = readInput().strip()
        if username == "0":
            return None
        drawScreen(loginInterface("[muted]Username:[/muted] " + escape(username), "Password"), True)
        password = readInput(True)
        account = auth.login(username, password)
        if account is not None:
            loadingBar("Logging in...")
            return user(account[0], account[1])
        left = max_attempts - attempt - 1
        message = "[bad]Error: Wrong username or password. Attempts left: " + str(left) + "[/bad]"
    startScreen("Login")
    addNote("[bad]Error: Too many failed attempts. Going back...[/bad]")
    pause()
    return None


def viewBooks():
    showTableScreen("Books  >  All books", reports.booksTable(dataManager.loadBooks()))


def addBookScreen():
    startScreen("Books  >  Add a book")
    addNote("[muted]Type 0 at any question to cancel.[/muted]")
    title = askText("Title")
    if title is None:
        return
    author = askText("Author")
    if author is None:
        return
    category = askText("Category (example: Fiction)")
    if category is None:
        return
    copies = askNumber("Number of copies (1-99)", 1, 99)
    if copies is None:
        return
    ok, message = dataManager.addBook(title, author, category, copies)
    showResult(ok, message)


def updateBookScreen():
    startScreen("Books  >  Update a book")
    addTable(reports.booksTable(dataManager.loadBooks()))
    addNote("[muted]Type 0 at any question to cancel.[/muted]")
    bookId = askText("Book ID to update")
    if bookId is None:
        return
    book = dataManager.findRecord(dataManager.loadBooks(), bookId)
    if book is None:
        showResult(False, "Book not found.")
        return
    addNote("[muted]Press Enter to keep the current value.[/muted]")
    title = askText("Title (now: " + book["title"] + ")", book["title"])
    if title is None:
        return
    author = askText("Author (now: " + book["author"] + ")", book["author"])
    if author is None:
        return
    category = askText("Category (now: " + book["category"] + ")", book["category"])
    if category is None:
        return
    copies = askNumber("Copies (now: " + str(book["copies"]) + ")", 1, 99, book["copies"])
    if copies is None:
        return
    ok, message = dataManager.updateBook(book["id"], title, author, category, copies)
    showResult(ok, message)


def deleteBookScreen(currentUser):
    if not requireAdmin(currentUser):
        return
    startScreen("Books  >  Delete a book")
    addTable(reports.booksTable(dataManager.loadBooks()))
    addNote("[muted]Type 0 to cancel.[/muted]")
    bookId = askText("Book ID to delete")
    if bookId is None:
        return
    book = dataManager.findRecord(dataManager.loadBooks(), bookId)
    if book is None:
        showResult(False, "Book not found.")
        return
    if askYesNo("Delete " + book["id"] + " - " + book["title"] + "?"):
        ok, message = dataManager.deleteBook(book["id"])
        showResult(ok, message)


def booksMenu(currentUser):
    while True:
        drawScreen(bookInterface(currentUser))
        choice = readInput()

        if choice == "1":
            viewBooks()
        elif choice == "2":
            addBookScreen()
        elif choice == "3":
            updateBookScreen()
        elif choice == "4":
            deleteBookScreen(currentUser)
        elif choice == "0":
            break
        else:
            invalidChoice()


def viewBorrowers():
    showTableScreen("Borrowers  >  All borrowers", reports.borrowersTable(dataManager.loadBorrowers()))


def addBorrowerScreen():
    startScreen("Borrowers  >  Add a borrower")
    addNote("[muted]Type 0 at any question to cancel.[/muted]")
    name = askText("Full name")
    if name is None:
        return
    contact = askText("Contact (phone or email)")
    if contact is None:
        return
    ok, message = dataManager.addBorrower(name, contact)
    showResult(ok, message)


def updateBorrowerScreen():
    startScreen("Borrowers  >  Update a borrower")
    addTable(reports.borrowersTable(dataManager.loadBorrowers()))
    addNote("[muted]Type 0 at any question to cancel.[/muted]")
    borrowerId = askText("Borrower ID to update")
    if borrowerId is None:
        return
    borrower = dataManager.findRecord(dataManager.loadBorrowers(), borrowerId)
    if borrower is None:
        showResult(False, "Borrower not found.")
        return
    addNote("[muted]Press Enter to keep the current value.[/muted]")
    name = askText("Name (now: " + borrower["name"] + ")", borrower["name"])
    if name is None:
        return
    contact = askText("Contact (now: " + borrower["contact"] + ")", borrower["contact"])
    if contact is None:
        return
    ok, message = dataManager.updateBorrower(borrower["id"], name, contact)
    showResult(ok, message)


def deleteBorrowerScreen(currentUser):
    if not requireAdmin(currentUser):
        return
    startScreen("Borrowers  >  Delete a borrower")
    addTable(reports.borrowersTable(dataManager.loadBorrowers()))
    addNote("[muted]Type 0 to cancel.[/muted]")
    borrowerId = askText("Borrower ID to delete")
    if borrowerId is None:
        return
    borrower = dataManager.findRecord(dataManager.loadBorrowers(), borrowerId)
    if borrower is None:
        showResult(False, "Borrower not found.")
        return
    if askYesNo("Delete " + borrower["id"] + " - " + borrower["name"] + "?"):
        ok, message = dataManager.deleteBorrower(borrower["id"])
        showResult(ok, message)


def borrowersMenu(currentUser):
    while True:
        drawScreen(borrowerInterface(currentUser))
        choice = readInput()

        if choice == "1":
            viewBorrowers()
        elif choice == "2":
            addBorrowerScreen()
        elif choice == "3":
            updateBorrowerScreen()
        elif choice == "4":
            deleteBorrowerScreen(currentUser)
        elif choice == "0":
            break
        else:
            invalidChoice()


def borrowBookScreen():
    startScreen("Borrow / Return  >  Borrow a book  (step 1 of 2)")
    addTable(reports.booksTable(dataManager.loadBooks()))
    addNote("[muted]Choose the book. Type 0 to cancel.[/muted]")
    bookId = askText("Book ID")
    if bookId is None:
        return
    book = dataManager.findRecord(dataManager.loadBooks(), bookId)
    if book is None:
        showResult(False, "Book not found.")
        return
    if book["available"] <= 0:
        showResult(False, "No copies of this book are available.")
        return
    startScreen("Borrow / Return  >  Borrow a book  (step 2 of 2)")
    addTable(reports.borrowersTable(dataManager.loadBorrowers()))
    addNote("[muted]Choose the borrower for [key]" + book["id"] + "[/key] " + escape(book["title"]) + ". Type 0 to cancel.[/muted]")
    borrowerId = askText("Borrower ID")
    if borrowerId is None:
        return
    days = askNumber("Loan days (Enter = " + str(dataManager.loan_days) + ")", 1, 30, dataManager.loan_days)
    if days is None:
        return
    ok, message = dataManager.borrowBook(book["id"], borrowerId, days)
    showResult(ok, message)


def returnBookScreen():
    startScreen("Borrow / Return  >  Return a book")
    addTable(reports.borrowedReport())
    addNote("[muted]Type the Record ID (example: H006). Type 0 to cancel.[/muted]")
    recordId = askText("Record ID to return")
    if recordId is None:
        return
    ok, message = dataManager.returnBook(recordId)
    showResult(ok, message)


def historyScreen():
    showTableScreen("Borrow / Return  >  Borrowing history", reports.historyTable(dataManager.loadHistory()))


def extendScreen():
    startScreen("Borrow / Return  >  Extend a due date")
    addTable(reports.borrowedReport())
    addNote("[muted]Type 0 to cancel.[/muted]")
    recordId = askText("Record ID to extend")
    if recordId is None:
        return
    extra = askNumber("Extra days (1-" + str(dataManager.max_extend_days) + ")", 1, dataManager.max_extend_days)
    if extra is None:
        return
    ok, message = dataManager.extendDueDate(recordId, extra)
    showResult(ok, message)


def deleteRecordScreen(currentUser):
    if not requireAdmin(currentUser):
        return
    startScreen("Borrow / Return  >  Delete a history record")
    addTable(reports.historyTable(dataManager.loadHistory()))
    addNote("[muted]Only returned records can be deleted. Type 0 to cancel.[/muted]")
    recordId = askText("Record ID to delete")
    if recordId is None:
        return
    if askYesNo("Delete record " + recordId.upper() + "?"):
        ok, message = dataManager.deleteHistory(recordId)
        showResult(ok, message)


def borrowMenu(currentUser):
    while True:
        drawScreen(borrowInterface(currentUser))
        choice = readInput()

        if choice == "1":
            borrowBookScreen()
        elif choice == "2":
            returnBookScreen()
        elif choice == "3":
            historyScreen()
        elif choice == "4":
            extendScreen()
        elif choice == "5":
            deleteRecordScreen(currentUser)
        elif choice == "0":
            break
        else:
            invalidChoice()


def searchBooksScreen():
    startScreen("Search  >  Books")
    addNote("[muted]Type part of a title, author, category or ID. Type 0 to cancel.[/muted]")
    keyword = askText("Search books")
    if keyword is None:
        return
    results = dataManager.searchBooks(keyword)
    addTable(reports.booksTable(results, "Book results for '" + keyword + "'"))
    pause()


def searchBorrowersScreen():
    startScreen("Search  >  Borrowers")
    addNote("[muted]Type part of a name, ID or contact. Type 0 to cancel.[/muted]")
    keyword = askText("Search borrowers")
    if keyword is None:
        return
    results = dataManager.searchBorrowers(keyword)
    addTable(reports.borrowersTable(results, "Borrower results for '" + keyword + "'"))
    pause()


def searchHistoryScreen():
    startScreen("Search  >  Borrowing records")
    addNote("[muted]Type a status (borrowed, overdue, returned), a book title or a borrower name. Type 0 to cancel.[/muted]")
    keyword = askText("Search records")
    if keyword is None:
        return
    results = dataManager.searchHistory(keyword)
    addTable(reports.historyTable(results, "Record results for '" + keyword + "'"))
    pause()


def searchMenu():
    while True:
        drawScreen(searchInterface())
        choice = readInput()

        if choice == "1":
            searchBooksScreen()
        elif choice == "2":
            searchBorrowersScreen()
        elif choice == "3":
            searchHistoryScreen()
        elif choice == "0":
            break
        else:
            invalidChoice()


def reportsMenu():
    while True:
        drawScreen(reportInterface())
        choice = readInput()

        if choice == "1":
            showTableScreen("Reports  >  Borrowed / overdue", reports.borrowedReport())
        elif choice == "2":
            showTableScreen("Reports  >  Most borrowed", reports.mostBorrowedReport())
        elif choice == "3":
            showTableScreen("Reports  >  By category", reports.categoryReport())
        elif choice == "4":
            showTableScreen("Reports  >  Borrower activity", reports.borrowerActivityReport())
        elif choice == "0":
            break
        else:
            invalidChoice()
