from rich import box
from rich.table import Table

import dataManager


# make an empty table with the theme colors
def makeTable(title, caption=""):
    return Table(
        title=title,
        caption=caption,
        box=box.ROUNDED,
        border_style="border",
        header_style="accent",
        title_style="accent",
        caption_style="muted",
        style="main",
        padding=(0, 1),
    )


# status text with color
def statusText(status):
    if status == "Returned":
        return "[good]Returned[/good]"
    if status == "Overdue":
        return "[bad]Overdue[/bad]"
    return "[warn]Borrowed[/warn]"


def booksTable(books, title="Books"):
    table = makeTable(title, str(len(books)) + " record(s)")
    table.add_column("ID", style="key")
    table.add_column("Title")
    table.add_column("Author")
    table.add_column("Category")
    table.add_column("Copies", justify="right")
    table.add_column("Available", justify="right")
    for book in books:
        if book["available"] == 0:
            available = "[bad]0[/bad]"
        else:
            available = str(book["available"])
        table.add_row(book["id"], book["title"], book["author"], book["category"], str(book["copies"]), available)
    return table


def borrowersTable(borrowers, title="Borrowers"):
    history = dataManager.loadHistory()
    table = makeTable(title, str(len(borrowers)) + " record(s)")
    table.add_column("ID", style="key")
    table.add_column("Name")
    table.add_column("Contact")
    table.add_column("Registered")
    table.add_column("Active Loans", justify="right")
    for borrower in borrowers:
        active = dataManager.countActiveLoans(history, "borrower_id", borrower["id"])
        table.add_row(borrower["id"], borrower["name"], borrower["contact"], borrower["date_registered"], str(active))
    return table


def historyTable(records, title="Borrowing History"):
    titles = dataManager.getBookTitles()
    names = dataManager.getBorrowerNames()
    table = makeTable(title, str(len(records)) + " record(s)")
    table.add_column("ID", style="key")
    table.add_column("Book")
    table.add_column("Borrower")
    table.add_column("Borrowed")
    table.add_column("Due")
    table.add_column("Returned")
    table.add_column("Status")
    for record in records:
        table.add_row(
            record["id"],
            titles.get(record["book_id"], "(deleted book)"),
            names.get(record["borrower_id"], "(deleted borrower)"),
            record["date_borrowed"],
            record["due_date"],
            record["date_returned"],
            statusText(dataManager.getStatus(record)),
        )
    return table


def usersTable(users, title="System Users"):
    table = makeTable(title, str(len(users)) + " user(s)")
    table.add_column("Username", style="key")
    table.add_column("Role")
    for user in users:
        table.add_row(user["username"], user["role"])
    return table
