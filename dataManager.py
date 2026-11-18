import os
from datetime import date, timedelta

# file names
BOOKS_FILE = "books.txt"
BORROWERS_FILE = "borrowers.txt"
HISTORY_FILE = "borrow_history.txt"
SETTINGS_FILE = "settings.txt"

# fields of each file, same order as the columns
BOOK_FIELDS = ["id", "title", "author", "category", "copies", "available"]
BOOK_NUMBERS = ["copies", "available"]
BORROWER_FIELDS = ["id", "name", "contact", "date_registered"]
HISTORY_FIELDS = ["id", "book_id", "borrower_id", "date_borrowed", "due_date", "date_returned", "status"]

# library rules
loan_days = 7
max_loans = 3
max_extend_days = 30

# file problems are saved here
fileErrors = []


# get the path of a file in the program folder
def filePath(fileName):
    folder = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(folder, fileName)


# remove the characters that break the file or rich
def cleanText(text):
    text = str(text).strip()
    text = text.replace("|", "/")
    text = text.replace("[", "(")
    text = text.replace("]", ")")
    return text


# today as text
def todayText():
    return str(date.today())


# change text to a date, None if it is not valid
def parseDate(text):
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


# read a file, returns the records and how many lines were skipped
def readRecords(fileName, fields, numberFields=[]):
    records = []
    skipped = 0
    path = filePath(fileName)
    try:
        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except FileNotFoundError:
        # make an empty file if it is missing
        try:
            open(path, "w", encoding="utf-8").close()
        except OSError:
            fileErrors.append("Could not create " + fileName)
        return records, skipped
    except PermissionError:
        fileErrors.append("Permission denied: " + fileName)
        return records, skipped
    except OSError:
        fileErrors.append("Could not read " + fileName)
        return records, skipped

    for line in lines:
        line = line.strip()
        if line == "":
            continue
        parts = line.split("|")
        if len(parts) != len(fields):
            skipped = skipped + 1
            continue
        record = {}
        for index in range(len(fields)):
            record[fields[index]] = parts[index]
        try:
            for name in numberFields:
                record[name] = int(record[name])
        except ValueError:
            skipped = skipped + 1
            continue
        records.append(record)
    return records, skipped


# write all the records to the file, True if it worked
def saveRecords(fileName, fields, records):
    try:
        with open(filePath(fileName), "w", encoding="utf-8") as file:
            for record in records:
                values = []
                for name in fields:
                    values.append(str(record[name]))
                file.write("|".join(values) + "\n")
        return True
    except OSError:
        return False


# add one record at the end of the file
def appendRecord(fileName, fields, record):
    path = filePath(fileName)
    try:
        prefix = ""
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file:
                text = file.read()
            # add a new line first if the file does not end with one
            if text != "" and not text.endswith("\n"):
                prefix = "\n"
        values = []
        for name in fields:
            values.append(str(record[name]))
        with open(path, "a", encoding="utf-8") as file:
            file.write(prefix + "|".join(values) + "\n")
        return True
    except OSError:
        return False


# get the next id like B001, B002
def nextId(records, prefix):
    highest = 0
    for record in records:
        number = record["id"][len(prefix):]
        if record["id"].startswith(prefix) and number.isdigit():
            if int(number) > highest:
                highest = int(number)
    return prefix + str(highest + 1).zfill(3)


# find a record by id, None if not found
def findRecord(records, recordId):
    for record in records:
        if record["id"].lower() == recordId.strip().lower():
            return record
    return None


def loadBooks():
    return readRecords(BOOKS_FILE, BOOK_FIELDS, BOOK_NUMBERS)[0]


def saveBooks(books):
    return saveRecords(BOOKS_FILE, BOOK_FIELDS, books)


def loadBorrowers():
    return readRecords(BORROWERS_FILE, BORROWER_FIELDS)[0]


def saveBorrowers(borrowers):
    return saveRecords(BORROWERS_FILE, BORROWER_FIELDS, borrowers)


def loadHistory():
    return readRecords(HISTORY_FILE, HISTORY_FIELDS)[0]


def saveHistory(history):
    return saveRecords(HISTORY_FILE, HISTORY_FIELDS, history)


# book id and title, used in the tables
def getBookTitles():
    titles = {}
    for book in loadBooks():
        titles[book["id"]] = book["title"]
    return titles


# borrower id and name
def getBorrowerNames():
    names = {}
    for borrower in loadBorrowers():
        names[borrower["id"]] = borrower["name"]
    return names


# Returned, Overdue or Borrowed
# overdue is not in the file, it comes from the due date
def getStatus(record):
    if record["status"] == "Returned":
        return "Returned"
    dueDate = parseDate(record["due_date"])
    if dueDate is not None and dueDate < date.today():
        return "Overdue"
    return "Borrowed"


# days late, 0 if not late or returned
def daysLate(record):
    dueDate = parseDate(record["due_date"])
    if record["status"] == "Returned" or dueDate is None:
        return 0
    late = (date.today() - dueDate).days
    if late > 0:
        return late
    return 0


# count the loans not returned yet (field is book_id or borrower_id)
def countActiveLoans(history, field, itemId):
    count = 0
    for record in history:
        if record[field] == itemId and record["status"] != "Returned":
            count = count + 1
    return count


# add a book, returns True/False and a message
def addBook(title, author, category, copies):
    books = loadBooks()
    title = cleanText(title)
    author = cleanText(author)
    category = cleanText(category)
    if title == "" or author == "" or category == "":
        return False, "Title, author and category cannot be empty."
    if copies < 1:
        return False, "Copies must be at least 1."
    for book in books:
        if book["title"].lower() == title.lower() and book["author"].lower() == author.lower():
            return False, "This book already exists (" + book["id"] + ")."
    record = {
        "id": nextId(books, "B"),
        "title": title,
        "author": author,
        "category": category,
        "copies": copies,
        "available": copies,
    }
    if appendRecord(BOOKS_FILE, BOOK_FIELDS, record):
        return True, "Book added with ID " + record["id"] + "."
    return False, "Could not save the book (file error)."


# update a book, available is worked out again
def updateBook(bookId, title, author, category, copies):
    books = loadBooks()
    book = findRecord(books, bookId)
    if book is None:
        return False, "Book not found."
    title = cleanText(title)
    author = cleanText(author)
    category = cleanText(category)
    if title == "" or author == "" or category == "":
        return False, "Title, author and category cannot be empty."
    active = countActiveLoans(loadHistory(), "book_id", book["id"])
    if copies < active:
        return False, "Copies cannot be less than the " + str(active) + " copy(ies) currently borrowed."
    book["title"] = title
    book["author"] = author
    book["category"] = category
    book["copies"] = copies
    book["available"] = copies - active
    if saveBooks(books):
        return True, "Book " + book["id"] + " updated."
    return False, "Could not save the changes (file error)."


# delete a book if no copies are borrowed
def deleteBook(bookId):
    books = loadBooks()
    book = findRecord(books, bookId)
    if book is None:
        return False, "Book not found."
    active = countActiveLoans(loadHistory(), "book_id", book["id"])
    if active > 0:
        return False, "Cannot delete: this book has " + str(active) + " active loan(s)."
    books.remove(book)
    if saveBooks(books):
        return True, "Book " + book["id"] + " deleted."
    return False, "Could not save the changes (file error)."


def addBorrower(name, contact):
    borrowers = loadBorrowers()
    name = cleanText(name)
    contact = cleanText(contact)
    if name == "" or contact == "":
        return False, "Name and contact cannot be empty."
    for borrower in borrowers:
        if borrower["name"].lower() == name.lower() and borrower["contact"] == contact:
            return False, "This borrower already exists (" + borrower["id"] + ")."
    record = {
        "id": nextId(borrowers, "BR"),
        "name": name,
        "contact": contact,
        "date_registered": todayText(),
    }
    if appendRecord(BORROWERS_FILE, BORROWER_FIELDS, record):
        return True, "Borrower added with ID " + record["id"] + "."
    return False, "Could not save the borrower (file error)."


def updateBorrower(borrowerId, name, contact):
    borrowers = loadBorrowers()
    borrower = findRecord(borrowers, borrowerId)
    if borrower is None:
        return False, "Borrower not found."
    name = cleanText(name)
    contact = cleanText(contact)
    if name == "" or contact == "":
        return False, "Name and contact cannot be empty."
    borrower["name"] = name
    borrower["contact"] = contact
    if saveBorrowers(borrowers):
        return True, "Borrower " + borrower["id"] + " updated."
    return False, "Could not save the changes (file error)."


# delete a borrower if they have no books
def deleteBorrower(borrowerId):
    borrowers = loadBorrowers()
    borrower = findRecord(borrowers, borrowerId)
    if borrower is None:
        return False, "Borrower not found."
    active = countActiveLoans(loadHistory(), "borrower_id", borrower["id"])
    if active > 0:
        return False, "Cannot delete: this borrower has " + str(active) + " active loan(s)."
    borrowers.remove(borrower)
    if saveBorrowers(borrowers):
        return True, "Borrower " + borrower["id"] + " deleted."
    return False, "Could not save the changes (file error)."


# borrow a book, check the rules first
def borrowBook(bookId, borrowerId, days=loan_days):
    books = loadBooks()
    borrowers = loadBorrowers()
    history = loadHistory()
    book = findRecord(books, bookId)
    borrower = findRecord(borrowers, borrowerId)
    if book is None:
        return False, "Book not found."
    if borrower is None:
        return False, "Borrower not found."
    if book["available"] <= 0:
        return False, "No copies of this book are available."

    # check the loans of the borrower
    loans = 0
    for record in history:
        if record["borrower_id"] == borrower["id"] and record["status"] != "Returned":
            loans = loans + 1
            if getStatus(record) == "Overdue":
                return False, "This borrower has an overdue book. Return it first."
            if record["book_id"] == book["id"]:
                return False, "This borrower already has this book."
    if loans >= max_loans:
        return False, "This borrower already has " + str(max_loans) + " books (the limit)."

    record = {
        "id": nextId(history, "H"),
        "book_id": book["id"],
        "borrower_id": borrower["id"],
        "date_borrowed": todayText(),
        "due_date": str(date.today() + timedelta(days=days)),
        "date_returned": "-",
        "status": "Borrowed",
    }
    if not appendRecord(HISTORY_FILE, HISTORY_FIELDS, record):
        return False, "Could not save the record (file error)."
    book["available"] = book["available"] - 1
    if not saveBooks(books):
        return False, "Could not update the book copies (file error)."
    return True, "Borrowed! Record " + record["id"] + ", due on " + record["due_date"] + "."


# return a book and give the copy back
def returnBook(recordId):
    history = loadHistory()
    books = loadBooks()
    record = findRecord(history, recordId)
    if record is None:
        return False, "Record not found."
    if record["status"] == "Returned":
        return False, "This book was already returned."
    late = daysLate(record)
    record["date_returned"] = todayText()
    record["status"] = "Returned"
    book = findRecord(books, record["book_id"])
    if book is not None and book["available"] < book["copies"]:
        book["available"] = book["available"] + 1
        if not saveBooks(books):
            return False, "Could not update the book copies (file error)."
    if not saveHistory(history):
        return False, "Could not save the record (file error)."
    if late > 0:
        return True, "Returned " + str(late) + " day(s) late."
    return True, "Book returned on time. Thank you!"


# move the due date later
def extendDueDate(recordId, extraDays):
    history = loadHistory()
    record = findRecord(history, recordId)
    if record is None:
        return False, "Record not found."
    if record["status"] == "Returned":
        return False, "This book was already returned."
    dueDate = parseDate(record["due_date"])
    if dueDate is None:
        return False, "This record has an invalid due date."
    if extraDays < 1 or extraDays > max_extend_days:
        return False, "Extra days must be from 1 to " + str(max_extend_days) + "."
    record["due_date"] = str(dueDate + timedelta(days=extraDays))
    if saveHistory(history):
        return True, "New due date: " + record["due_date"] + "."
    return False, "Could not save the changes (file error)."


# delete a returned record
def deleteHistory(recordId):
    history = loadHistory()
    record = findRecord(history, recordId)
    if record is None:
        return False, "Record not found."
    if record["status"] != "Returned":
        return False, "Return the book first before deleting this record."
    history.remove(record)
    if saveHistory(history):
        return True, "Record " + record["id"] + " deleted."
    return False, "Could not save the changes (file error)."


def searchBooks(keyword):
    keyword = keyword.strip().lower()
    results = []
    for book in loadBooks():
        text = book["id"] + " " + book["title"] + " " + book["author"] + " " + book["category"]
        if keyword in text.lower():
            results.append(book)
    return results


def searchBorrowers(keyword):
    keyword = keyword.strip().lower()
    results = []
    for borrower in loadBorrowers():
        text = borrower["id"] + " " + borrower["name"] + " " + borrower["contact"]
        if keyword in text.lower():
            results.append(borrower)
    return results


# search records by id, book, borrower or status
def searchHistory(keyword):
    keyword = keyword.strip().lower()
    titles = getBookTitles()
    names = getBorrowerNames()
    results = []
    for record in loadHistory():
        text = record["id"] + " " + record["book_id"] + " " + record["borrower_id"] + " " + getStatus(record)
        text = text + " " + titles.get(record["book_id"], "") + " " + names.get(record["borrower_id"], "")
        if keyword in text.lower():
            results.append(record)
    return results


# settings.txt has lines like theme=Purple Cyan
def loadSettings():
    settings = {"theme": "Purple Cyan"}
    try:
        with open(filePath(SETTINGS_FILE), "r", encoding="utf-8") as file:
            for line in file:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    settings[key.strip()] = value.strip()
    except FileNotFoundError:
        saveSettings(settings)
    except OSError:
        pass
    return settings


def saveSettings(settings):
    try:
        with open(filePath(SETTINGS_FILE), "w", encoding="utf-8") as file:
            for key in settings:
                file.write(key + "=" + str(settings[key]) + "\n")
        return True
    except OSError:
        return False


# read every file once, returns the counts and the problems
def checkFiles():
    fileErrors.clear()
    counts = {}
    problems = []
    fileList = [
        ("books", BOOKS_FILE, BOOK_FIELDS, BOOK_NUMBERS),
        ("borrowers", BORROWERS_FILE, BORROWER_FIELDS, []),
        ("history", HISTORY_FILE, HISTORY_FIELDS, []),
    ]
    for name, fileName, fields, numbers in fileList:
        records, skipped = readRecords(fileName, fields, numbers)
        counts[name] = len(records)
        if skipped > 0:
            problems.append(str(skipped) + " corrupted line(s) skipped in " + fileName)
    loadSettings()
    problems = problems + fileErrors
    return counts, problems


# Returned, Overdue or Borrowed
# overdue is not in the file, it comes from the due date
def getStatus(record):
    if record["status"] == "Returned":
        return "Returned"
    dueDate = parseDate(record["due_date"])
    if dueDate is not None and dueDate < date.today():
        return "Overdue"
    return "Borrowed"


# days late, 0 if not late or returned
def daysLate(record):
    dueDate = parseDate(record["due_date"])
    if record["status"] == "Returned" or dueDate is None:
        return 0
    late = (date.today() - dueDate).days
    if late > 0:
        return late
    return 0


# count the loans not returned yet (field is book_id or borrower_id)
def countActiveLoans(history, field, itemId):
    count = 0
    for record in history:
        if record[field] == itemId and record["status"] != "Returned":
            count = count + 1
    return count


# add a book, returns True/False and a message
def addBook(title, author, category, copies):
    books = loadBooks()
    title = cleanText(title)
    author = cleanText(author)
    category = cleanText(category)
    if title == "" or author == "" or category == "":
        return False, "Title, author and category cannot be empty."
    if copies < 1:
        return False, "Copies must be at least 1."
    for book in books:
        if book["title"].lower() == title.lower() and book["author"].lower() == author.lower():
            return False, "This book already exists (" + book["id"] + ")."
    record = {
        "id": nextId(books, "B"),
        "title": title,
        "author": author,
        "category": category,
        "copies": copies,
        "available": copies,
    }
    if appendRecord(BOOKS_FILE, BOOK_FIELDS, record):
        return True, "Book added with ID " + record["id"] + "."
    return False, "Could not save the book (file error)."


# update a book, available is worked out again
def updateBook(bookId, title, author, category, copies):
    books = loadBooks()
    book = findRecord(books, bookId)
    if book is None:
        return False, "Book not found."
    title = cleanText(title)
    author = cleanText(author)
    category = cleanText(category)
    if title == "" or author == "" or category == "":
        return False, "Title, author and category cannot be empty."
    active = countActiveLoans(loadHistory(), "book_id", book["id"])
    if copies < active:
        return False, "Copies cannot be less than the " + str(active) + " copy(ies) currently borrowed."
    book["title"] = title
    book["author"] = author
    book["category"] = category
    book["copies"] = copies
    book["available"] = copies - active
    if saveBooks(books):
        return True, "Book " + book["id"] + " updated."
    return False, "Could not save the changes (file error)."


# delete a book if no copies are borrowed
def deleteBook(bookId):
    books = loadBooks()
    book = findRecord(books, bookId)
    if book is None:
        return False, "Book not found."
    active = countActiveLoans(loadHistory(), "book_id", book["id"])
    if active > 0:
        return False, "Cannot delete: this book has " + str(active) + " active loan(s)."
    books.remove(book)
    if saveBooks(books):
        return True, "Book " + book["id"] + " deleted."
    return False, "Could not save the changes (file error)."


def addBorrower(name, contact):
    borrowers = loadBorrowers()
    name = cleanText(name)
    contact = cleanText(contact)
    if name == "" or contact == "":
        return False, "Name and contact cannot be empty."
    for borrower in borrowers:
        if borrower["name"].lower() == name.lower() and borrower["contact"] == contact:
            return False, "This borrower already exists (" + borrower["id"] + ")."
    record = {
        "id": nextId(borrowers, "BR"),
        "name": name,
        "contact": contact,
        "date_registered": todayText(),
    }
    if appendRecord(BORROWERS_FILE, BORROWER_FIELDS, record):
        return True, "Borrower added with ID " + record["id"] + "."
    return False, "Could not save the borrower (file error)."


def updateBorrower(borrowerId, name, contact):
    borrowers = loadBorrowers()
    borrower = findRecord(borrowers, borrowerId)
    if borrower is None:
        return False, "Borrower not found."
    name = cleanText(name)
    contact = cleanText(contact)
    if name == "" or contact == "":
        return False, "Name and contact cannot be empty."
    borrower["name"] = name
    borrower["contact"] = contact
    if saveBorrowers(borrowers):
        return True, "Borrower " + borrower["id"] + " updated."
    return False, "Could not save the changes (file error)."


# delete a borrower if they have no books
def deleteBorrower(borrowerId):
    borrowers = loadBorrowers()
    borrower = findRecord(borrowers, borrowerId)
    if borrower is None:
        return False, "Borrower not found."
    active = countActiveLoans(loadHistory(), "borrower_id", borrower["id"])
    if active > 0:
        return False, "Cannot delete: this borrower has " + str(active) + " active loan(s)."
    borrowers.remove(borrower)
    if saveBorrowers(borrowers):
        return True, "Borrower " + borrower["id"] + " deleted."
    return False, "Could not save the changes (file error)."


# borrow a book, check the rules first
def borrowBook(bookId, borrowerId, days=loan_days):
    books = loadBooks()
    borrowers = loadBorrowers()
    history = loadHistory()
    book = findRecord(books, bookId)
    borrower = findRecord(borrowers, borrowerId)
    if book is None:
        return False, "Book not found."
    if borrower is None:
        return False, "Borrower not found."
    if book["available"] <= 0:
        return False, "No copies of this book are available."

    # check the loans of the borrower
    loans = 0
    for record in history:
        if record["borrower_id"] == borrower["id"] and record["status"] != "Returned":
            loans = loans + 1
            if getStatus(record) == "Overdue":
                return False, "This borrower has an overdue book. Return it first."
            if record["book_id"] == book["id"]:
                return False, "This borrower already has this book."
    if loans >= max_loans:
        return False, "This borrower already has " + str(max_loans) + " books (the limit)."

    record = {
        "id": nextId(history, "H"),
        "book_id": book["id"],
        "borrower_id": borrower["id"],
        "date_borrowed": todayText(),
        "due_date": str(date.today() + timedelta(days=days)),
        "date_returned": "-",
        "status": "Borrowed",
    }
    if not appendRecord(HISTORY_FILE, HISTORY_FIELDS, record):
        return False, "Could not save the record (file error)."
    book["available"] = book["available"] - 1
    if not saveBooks(books):
        return False, "Could not update the book copies (file error)."
    return True, "Borrowed! Record " + record["id"] + ", due on " + record["due_date"] + "."


# return a book and give the copy back
def returnBook(recordId):
    history = loadHistory()
    books = loadBooks()
    record = findRecord(history, recordId)
    if record is None:
        return False, "Record not found."
    if record["status"] == "Returned":
        return False, "This book was already returned."
    late = daysLate(record)
    record["date_returned"] = todayText()
    record["status"] = "Returned"
    book = findRecord(books, record["book_id"])
    if book is not None and book["available"] < book["copies"]:
        book["available"] = book["available"] + 1
        if not saveBooks(books):
            return False, "Could not update the book copies (file error)."
    if not saveHistory(history):
        return False, "Could not save the record (file error)."
    if late > 0:
        return True, "Returned " + str(late) + " day(s) late."
    return True, "Book returned on time. Thank you!"


# move the due date later
def extendDueDate(recordId, extraDays):
    history = loadHistory()
    record = findRecord(history, recordId)
    if record is None:
        return False, "Record not found."
    if record["status"] == "Returned":
        return False, "This book was already returned."
    dueDate = parseDate(record["due_date"])
    if dueDate is None:
        return False, "This record has an invalid due date."
    if extraDays < 1 or extraDays > max_extend_days:
        return False, "Extra days must be from 1 to " + str(max_extend_days) + "."
    record["due_date"] = str(dueDate + timedelta(days=extraDays))
    if saveHistory(history):
        return True, "New due date: " + record["due_date"] + "."
    return False, "Could not save the changes (file error)."


# delete a returned record
def deleteHistory(recordId):
    history = loadHistory()
    record = findRecord(history, recordId)
    if record is None:
        return False, "Record not found."
    if record["status"] != "Returned":
        return False, "Return the book first before deleting this record."
    history.remove(record)
    if saveHistory(history):
        return True, "Record " + record["id"] + " deleted."
    return False, "Could not save the changes (file error)."


def searchBooks(keyword):
    keyword = keyword.strip().lower()
    results = []
    for book in loadBooks():
        text = book["id"] + " " + book["title"] + " " + book["author"] + " " + book["category"]
        if keyword in text.lower():
            results.append(book)
    return results


def searchBorrowers(keyword):
    keyword = keyword.strip().lower()
    results = []
    for borrower in loadBorrowers():
        text = borrower["id"] + " " + borrower["name"] + " " + borrower["contact"]
        if keyword in text.lower():
            results.append(borrower)
    return results


# search records by id, book, borrower or status
def searchHistory(keyword):
    keyword = keyword.strip().lower()
    titles = getBookTitles()
    names = getBorrowerNames()
    results = []
    for record in loadHistory():
        text = record["id"] + " " + record["book_id"] + " " + record["borrower_id"] + " " + getStatus(record)
        text = text + " " + titles.get(record["book_id"], "") + " " + names.get(record["borrower_id"], "")
        if keyword in text.lower():
            results.append(record)
    return results


# settings.txt has lines like theme=Purple Cyan
def loadSettings():
    settings = {"theme": "Purple Cyan"}
    try:
        with open(filePath(SETTINGS_FILE), "r", encoding="utf-8") as file:
            for line in file:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    settings[key.strip()] = value.strip()
    except FileNotFoundError:
        saveSettings(settings)
    except OSError:
        pass
    return settings


def saveSettings(settings):
    try:
        with open(filePath(SETTINGS_FILE), "w", encoding="utf-8") as file:
            for key in settings:
                file.write(key + "=" + str(settings[key]) + "\n")
        return True
    except OSError:
        return False


# read every file once, returns the counts and the problems
def checkFiles():
    fileErrors.clear()
    counts = {}
    problems = []
    fileList = [
        ("books", BOOKS_FILE, BOOK_FIELDS, BOOK_NUMBERS),
        ("borrowers", BORROWERS_FILE, BORROWER_FIELDS, []),
        ("history", HISTORY_FILE, HISTORY_FIELDS, []),
    ]
    for name, fileName, fields, numbers in fileList:
        records, skipped = readRecords(fileName, fields, numbers)
        counts[name] = len(records)
        if skipped > 0:
            problems.append(str(skipped) + " corrupted line(s) skipped in " + fileName)
    loadSettings()
    problems = problems + fileErrors
    return counts, problems


# borrow a book, check the rules first
def borrowBook(bookId, borrowerId, days=loan_days):
    books = loadBooks()
    borrowers = loadBorrowers()
    history = loadHistory()
    book = findRecord(books, bookId)
    borrower = findRecord(borrowers, borrowerId)
    if book is None:
        return False, "Book not found."
    if borrower is None:
        return False, "Borrower not found."
    if book["available"] <= 0:
        return False, "No copies of this book are available."

    # check the loans of the borrower
    loans = 0
    for record in history:
        if record["borrower_id"] == borrower["id"] and record["status"] != "Returned":
            loans = loans + 1
            if getStatus(record) == "Overdue":
                return False, "This borrower has an overdue book. Return it first."
            if record["book_id"] == book["id"]:
                return False, "This borrower already has this book."
    if loans >= max_loans:
        return False, "This borrower already has " + str(max_loans) + " books (the limit)."

    record = {
        "id": nextId(history, "H"),
        "book_id": book["id"],
        "borrower_id": borrower["id"],
        "date_borrowed": todayText(),
        "due_date": str(date.today() + timedelta(days=days)),
        "date_returned": "-",
        "status": "Borrowed",
    }
    if not appendRecord(HISTORY_FILE, HISTORY_FIELDS, record):
        return False, "Could not save the record (file error)."
    book["available"] = book["available"] - 1
    if not saveBooks(books):
        return False, "Could not update the book copies (file error)."
    return True, "Borrowed! Record " + record["id"] + ", due on " + record["due_date"] + "."


# return a book and give the copy back
def returnBook(recordId):
    history = loadHistory()
    books = loadBooks()
    record = findRecord(history, recordId)
    if record is None:
        return False, "Record not found."
    if record["status"] == "Returned":
        return False, "This book was already returned."
    late = daysLate(record)
    record["date_returned"] = todayText()
    record["status"] = "Returned"
    book = findRecord(books, record["book_id"])
    if book is not None and book["available"] < book["copies"]:
        book["available"] = book["available"] + 1
        if not saveBooks(books):
            return False, "Could not update the book copies (file error)."
    if not saveHistory(history):
        return False, "Could not save the record (file error)."
    if late > 0:
        return True, "Returned " + str(late) + " day(s) late."
    return True, "Book returned on time. Thank you!"


# move the due date later
def extendDueDate(recordId, extraDays):
    history = loadHistory()
    record = findRecord(history, recordId)
    if record is None:
        return False, "Record not found."
    if record["status"] == "Returned":
        return False, "This book was already returned."
    dueDate = parseDate(record["due_date"])
    if dueDate is None:
        return False, "This record has an invalid due date."
    if extraDays < 1 or extraDays > max_extend_days:
        return False, "Extra days must be from 1 to " + str(max_extend_days) + "."
    record["due_date"] = str(dueDate + timedelta(days=extraDays))
    if saveHistory(history):
        return True, "New due date: " + record["due_date"] + "."
    return False, "Could not save the changes (file error)."


# delete a returned record
def deleteHistory(recordId):
    history = loadHistory()
    record = findRecord(history, recordId)
    if record is None:
        return False, "Record not found."
    if record["status"] != "Returned":
        return False, "Return the book first before deleting this record."
    history.remove(record)
    if saveHistory(history):
        return True, "Record " + record["id"] + " deleted."
    return False, "Could not save the changes (file error)."


def searchBooks(keyword):
    keyword = keyword.strip().lower()
    results = []
    for book in loadBooks():
        text = book["id"] + " " + book["title"] + " " + book["author"] + " " + book["category"]
        if keyword in text.lower():
            results.append(book)
    return results


def searchBorrowers(keyword):
    keyword = keyword.strip().lower()
    results = []
    for borrower in loadBorrowers():
        text = borrower["id"] + " " + borrower["name"] + " " + borrower["contact"]
        if keyword in text.lower():
            results.append(borrower)
    return results


# search records by id, book, borrower or status
def searchHistory(keyword):
    keyword = keyword.strip().lower()
    titles = getBookTitles()
    names = getBorrowerNames()
    results = []
    for record in loadHistory():
        text = record["id"] + " " + record["book_id"] + " " + record["borrower_id"] + " " + getStatus(record)
        text = text + " " + titles.get(record["book_id"], "") + " " + names.get(record["borrower_id"], "")
        if keyword in text.lower():
            results.append(record)
    return results


# settings.txt has lines like theme=Purple Cyan
def loadSettings():
    settings = {"theme": "Purple Cyan"}
    try:
        with open(filePath(SETTINGS_FILE), "r", encoding="utf-8") as file:
            for line in file:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    settings[key.strip()] = value.strip()
    except FileNotFoundError:
        saveSettings(settings)
    except OSError:
        pass
    return settings


def saveSettings(settings):
    try:
        with open(filePath(SETTINGS_FILE), "w", encoding="utf-8") as file:
            for key in settings:
                file.write(key + "=" + str(settings[key]) + "\n")
        return True
    except OSError:
        return False


# read every file once, returns the counts and the problems
def checkFiles():
    fileErrors.clear()
    counts = {}
    problems = []
    fileList = [
        ("books", BOOKS_FILE, BOOK_FIELDS, BOOK_NUMBERS),
        ("borrowers", BORROWERS_FILE, BORROWER_FIELDS, []),
        ("history", HISTORY_FILE, HISTORY_FIELDS, []),
    ]
    for name, fileName, fields, numbers in fileList:
        records, skipped = readRecords(fileName, fields, numbers)
        counts[name] = len(records)
        if skipped > 0:
            problems.append(str(skipped) + " corrupted line(s) skipped in " + fileName)
    loadSettings()
    problems = problems + fileErrors
    return counts, problems


# borrow a book, check the rules first
def borrowBook(bookId, borrowerId, days=loan_days):
    books = loadBooks()
    borrowers = loadBorrowers()
    history = loadHistory()
    book = findRecord(books, bookId)
    borrower = findRecord(borrowers, borrowerId)
    if book is None:
        return False, "Book not found."
    if borrower is None:
        return False, "Borrower not found."
    if book["available"] <= 0:
        return False, "No copies of this book are available."

    # check the loans of the borrower
    loans = 0
    for record in history:
        if record["borrower_id"] == borrower["id"] and record["status"] != "Returned":
            loans = loans + 1
            if getStatus(record) == "Overdue":
                return False, "This borrower has an overdue book. Return it first."
            if record["book_id"] == book["id"]:
                return False, "This borrower already has this book."
    if loans >= max_loans:
        return False, "This borrower already has " + str(max_loans) + " books (the limit)."

    record = {
        "id": nextId(history, "H"),
        "book_id": book["id"],
        "borrower_id": borrower["id"],
        "date_borrowed": todayText(),
        "due_date": str(date.today() + timedelta(days=days)),
        "date_returned": "-",
        "status": "Borrowed",
    }
    if not appendRecord(HISTORY_FILE, HISTORY_FIELDS, record):
        return False, "Could not save the record (file error)."
    book["available"] = book["available"] - 1
    if not saveBooks(books):
        return False, "Could not update the book copies (file error)."
    return True, "Borrowed! Record " + record["id"] + ", due on " + record["due_date"] + "."


# return a book and give the copy back
def returnBook(recordId):
    history = loadHistory()
    books = loadBooks()
    record = findRecord(history, recordId)
    if record is None:
        return False, "Record not found."
    if record["status"] == "Returned":
        return False, "This book was already returned."
    late = daysLate(record)
    record["date_returned"] = todayText()
    record["status"] = "Returned"
    book = findRecord(books, record["book_id"])
    if book is not None and book["available"] < book["copies"]:
        book["available"] = book["available"] + 1
        if not saveBooks(books):
            return False, "Could not update the book copies (file error)."
    if not saveHistory(history):
        return False, "Could not save the record (file error)."
    if late > 0:
        return True, "Returned " + str(late) + " day(s) late."
    return True, "Book returned on time. Thank you!"


# move the due date later
def extendDueDate(recordId, extraDays):
    history = loadHistory()
    record = findRecord(history, recordId)
    if record is None:
        return False, "Record not found."
    if record["status"] == "Returned":
        return False, "This book was already returned."
    dueDate = parseDate(record["due_date"])
    if dueDate is None:
        return False, "This record has an invalid due date."
    if extraDays < 1 or extraDays > max_extend_days:
        return False, "Extra days must be from 1 to " + str(max_extend_days) + "."
    record["due_date"] = str(dueDate + timedelta(days=extraDays))
    if saveHistory(history):
        return True, "New due date: " + record["due_date"] + "."
    return False, "Could not save the changes (file error)."


# delete a returned record
def deleteHistory(recordId):
    history = loadHistory()
    record = findRecord(history, recordId)
    if record is None:
        return False, "Record not found."
    if record["status"] != "Returned":
        return False, "Return the book first before deleting this record."
    history.remove(record)
    if saveHistory(history):
        return True, "Record " + record["id"] + " deleted."
    return False, "Could not save the changes (file error)."


def searchBooks(keyword):
    keyword = keyword.strip().lower()
    results = []
    for book in loadBooks():
        text = book["id"] + " " + book["title"] + " " + book["author"] + " " + book["category"]
        if keyword in text.lower():
            results.append(book)
    return results


def searchBorrowers(keyword):
    keyword = keyword.strip().lower()
    results = []
    for borrower in loadBorrowers():
        text = borrower["id"] + " " + borrower["name"] + " " + borrower["contact"]
        if keyword in text.lower():
            results.append(borrower)
    return results


# search records by id, book, borrower or status
def searchHistory(keyword):
    keyword = keyword.strip().lower()
    titles = getBookTitles()
    names = getBorrowerNames()
    results = []
    for record in loadHistory():
        text = record["id"] + " " + record["book_id"] + " " + record["borrower_id"] + " " + getStatus(record)
        text = text + " " + titles.get(record["book_id"], "") + " " + names.get(record["borrower_id"], "")
        if keyword in text.lower():
            results.append(record)
    return results


# settings.txt has lines like theme=Purple Cyan
def loadSettings():
    settings = {"theme": "Purple Cyan"}
    try:
        with open(filePath(SETTINGS_FILE), "r", encoding="utf-8") as file:
            for line in file:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    settings[key.strip()] = value.strip()
    except FileNotFoundError:
        saveSettings(settings)
    except OSError:
        pass
    return settings


def saveSettings(settings):
    try:
        with open(filePath(SETTINGS_FILE), "w", encoding="utf-8") as file:
            for key in settings:
                file.write(key + "=" + str(settings[key]) + "\n")
        return True
    except OSError:
        return False


# read every file once, returns the counts and the problems
def checkFiles():
    fileErrors.clear()
    counts = {}
    problems = []
    fileList = [
        ("books", BOOKS_FILE, BOOK_FIELDS, BOOK_NUMBERS),
        ("borrowers", BORROWERS_FILE, BORROWER_FIELDS, []),
        ("history", HISTORY_FILE, HISTORY_FIELDS, []),
    ]
    for name, fileName, fields, numbers in fileList:
        records, skipped = readRecords(fileName, fields, numbers)
        counts[name] = len(records)
        if skipped > 0:
            problems.append(str(skipped) + " corrupted line(s) skipped in " + fileName)
    loadSettings()
    problems = problems + fileErrors
    return counts, problems
