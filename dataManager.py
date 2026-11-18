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
