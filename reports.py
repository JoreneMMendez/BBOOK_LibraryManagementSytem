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


# count the numbers for the dashboard
def getSummary():
    books = dataManager.loadBooks()
    borrowers = dataManager.loadBorrowers()
    history = dataManager.loadHistory()
    copies = 0
    available = 0
    for book in books:
        copies = copies + book["copies"]
        available = available + book["available"]
    borrowed = 0
    overdue = 0
    for record in history:
        status = dataManager.getStatus(record)
        if status != "Returned":
            borrowed = borrowed + 1
        if status == "Overdue":
            overdue = overdue + 1
    return {
        "titles": len(books),
        "copies": copies,
        "available": available,
        "borrowed": borrowed,
        "borrowers": len(borrowers),
        "overdue": overdue,
    }


# books that are borrowed now, oldest due date first
def borrowedReport():
    titles = dataManager.getBookTitles()
    names = dataManager.getBorrowerNames()
    rows = []
    for record in dataManager.loadHistory():
        status = dataManager.getStatus(record)
        if status != "Returned":
            # due date is first so sort() sorts by it
            rows.append((
                record["due_date"],
                record["id"],
                titles.get(record["book_id"], "(deleted book)"),
                names.get(record["borrower_id"], "(deleted borrower)"),
                record["date_borrowed"],
                dataManager.daysLate(record),
                status,
            ))
    rows.sort()
    table = makeTable("Currently Borrowed / Overdue Books", str(len(rows)) + " active loan(s)")
    table.add_column("Record", style="key")
    table.add_column("Book")
    table.add_column("Borrower")
    table.add_column("Borrowed")
    table.add_column("Due")
    table.add_column("Days Late", justify="right")
    table.add_column("Status")
    for row in rows:
        if row[5] > 0:
            late = "[bad]" + str(row[5]) + "[/bad]"
        else:
            late = "0"
        table.add_row(row[1], row[2], row[3], row[4], row[0], late, statusText(row[6]))
    return table


# top 10 most borrowed books
def mostBorrowedReport():
    books = dataManager.loadBooks()
    counts = {}
    for record in dataManager.loadHistory():
        bookId = record["book_id"]
        counts[bookId] = counts.get(bookId, 0) + 1
    rows = []
    for bookId in counts:
        book = dataManager.findRecord(books, bookId)
        if book is not None:
            rows.append((counts[bookId], book["title"], book["author"], book["category"]))
    rows.sort(reverse=True)
    table = makeTable("Most Borrowed Books", "Top 10")
    table.add_column("Rank", justify="right")
    table.add_column("Title")
    table.add_column("Author")
    table.add_column("Category")
    table.add_column("Times Borrowed", justify="right")
    rank = 1
    for row in rows[:10]:
        table.add_row(str(rank), row[1], row[2], row[3], str(row[0]))
        rank = rank + 1
    return table


# books by category
def categoryReport():
    books = dataManager.loadBooks()
    # category name: [titles, copies, available, times borrowed]
    categories = {}
    for book in books:
        name = book["category"]
        if name not in categories:
            categories[name] = [0, 0, 0, 0]
        categories[name][0] = categories[name][0] + 1
        categories[name][1] = categories[name][1] + book["copies"]
        categories[name][2] = categories[name][2] + book["available"]
    for record in dataManager.loadHistory():
        book = dataManager.findRecord(books, record["book_id"])
        if book is not None:
            categories[book["category"]][3] = categories[book["category"]][3] + 1
    table = makeTable("Books by Category", str(len(categories)) + " categories")
    table.add_column("Category")
    table.add_column("Titles", justify="right")
    table.add_column("Copies", justify="right")
    table.add_column("Available", justify="right")
    table.add_column("Times Borrowed", justify="right")
    for name in sorted(categories):
        info = categories[name]
        table.add_row(name, str(info[0]), str(info[1]), str(info[2]), str(info[3]))
    return table


# how active each borrower is
def borrowerActivityReport():
    history = dataManager.loadHistory()
    rows = []
    for borrower in dataManager.loadBorrowers():
        total = 0
        returned = 0
        active = 0
        overdue = 0
        for record in history:
            if record["borrower_id"] == borrower["id"]:
                total = total + 1
                status = dataManager.getStatus(record)
                if status == "Returned":
                    returned = returned + 1
                else:
                    active = active + 1
                if status == "Overdue":
                    overdue = overdue + 1
        rows.append((total, borrower["name"], borrower["id"], returned, active, overdue))
    rows.sort(reverse=True)
    table = makeTable("Borrower Activity Summary", str(len(rows)) + " borrower(s)")
    table.add_column("Name")
    table.add_column("ID", style="key")
    table.add_column("Total Borrowed", justify="right")
    table.add_column("Returned", justify="right")
    table.add_column("Active", justify="right")
    table.add_column("Overdue", justify="right")
    for row in rows:
        if row[5] > 0:
            overdue = "[bad]" + str(row[5]) + "[/bad]"
        else:
            overdue = "0"
        table.add_row(row[1], row[2], str(row[0]), str(row[3]), str(row[4]), overdue)
    return table
