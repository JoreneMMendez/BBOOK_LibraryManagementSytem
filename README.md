# BBOOK Library Management System

A terminal-based Library Management System written in **Python 3** with **text file (.txt) storage**.
It has a classic old-school command-line feel, built with the `rich` library (panels, layouts, tables, colors and loading bars).
It manages **books**, **borrowers** and **borrowing history**, with login, roles, reports and color themes.

## Features

- **Login / logout** with two roles: **Administrator** and **Staff**
- **Salted password hashing** (`hashlib.pbkdf2_hmac` + `os.urandom` salt). No plain-text passwords are stored
- **Dashboard** with the BBOOK logo, a status bar (logged-in user, role, date, time) and cards for the library numbers (titles, available, borrowed, borrowers, overdue)
- **Books, Borrowers, Borrowing history**: add, view, update, delete (delete is Administrator only)
- **Linked records**
  - Borrowing lowers a book's available copies, returning raises it
  - A book with no copies left cannot be borrowed
  - A book or borrower with active loans cannot be deleted
  - Extra rules: max 3 books per borrower, no borrowing while a book is overdue, no borrowing the same book twice
- **Search** by title, author, category, ID, name, contact or status (partial and not case sensitive), shown in tables
- **Reports**: currently borrowed / overdue, most borrowed books, books by category, borrower activity
- **3 color themes** (Purple Cyan is the default, Amber Retro, Ocean Blue). The chosen theme is saved in `settings.txt`
- **Clean screens**: every screen is drawn inside one box, with the Input box inside it too. The terminal is cleared (including the old lines above) on every screen, so nothing scrolls up
- **User management** (Administrator): view, register, change role, reset password, delete
- **Update password** (verifies the old password, makes a new salt)
- **Error handling**: missing files are created, corrupted lines are skipped, invalid input is re-asked, file errors do not crash the program

## Requirements

- Python **3.10 or newer** (the program uses `match` / `case`)
- The `rich` library

## Installation

```bash
git clone <your-repository-link>
cd BBOOK_LibraryManagementSystem
pip install -r requirements.txt
```

## How to run

```bash
python Interface.py
```

Tips:
- Use a real terminal (Windows Terminal, PowerShell, macOS Terminal). Make the window about **100 columns x 40 rows** or bigger.
- In PyCharm, turn on **Run > Edit Configurations > Emulate terminal in output console**, or use the Terminal tab.
- At most questions, type `0` to cancel.

## Default login credentials

| Role | Username | Password |
|---|---|---|
| Administrator | `admin` | `admin123` |
| Staff | `staff` | `staff123` |

Change these passwords from **System Settings > Update my password**.
If `users.txt` is deleted, the program creates it again with the `admin` account.

## Staff vs Administrator

| Action | Staff | Administrator |
|---|---|---|
| Add / view / update books, borrowers | Yes | Yes |
| Borrow, return, extend, search, reports | Yes | Yes |
| Delete books, borrowers, history records | No | Yes |
| User management | No | Yes |
| Change theme / own password | Yes | Yes |

## File structure

```
BBOOK_LibraryManagementSystem/
├── Interface.py          # screens (Layouts), menus, input handling and main loop
├── auth.py               # login, salted hashing, user management
├── dataManager.py        # reading / writing .txt files, add/update/delete, borrow rules, search
├── reports.py            # rich tables, dashboard numbers, reports
├── themes.py             # theme dictionaries and apply function
├── users.txt             # username|role|salt|hash
├── books.txt             # book_id|title|author|category|copies|available
├── borrowers.txt         # borrower_id|name|contact|date_registered
├── borrow_history.txt    # record_id|book_id|borrower_id|date_borrowed|due_date|date_returned|status
├── settings.txt          # theme=Purple Cyan
├── requirements.txt
├── README.md
└── screenshots/
```

Notes about the data files:
- Fields are separated by `|`. The characters `|`, `[` and `]` are replaced when saving so they cannot break the files.
- Dates use the format `YYYY-MM-DD`.
- `Overdue` is not stored. It is worked out from the due date, so it updates by itself every day.
- A line that is damaged (wrong number of fields, bad number) is skipped when loading and a warning is shown at startup.
  It is removed the next time that file is saved.
