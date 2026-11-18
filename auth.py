import os
import hashlib

from dataManager import filePath, readRecords, saveRecords, appendRecord

# users.txt: username|role|salt|hash
USERS_FILE = "users.txt"
USER_FIELDS = ["username", "role", "salt", "hash"]

# the two roles
ROLES = ("Administrator", "Staff")

hash_rounds = 200000
default_admin = ("admin", "admin123")


# hash the password with a salt, returns (salt, hash)
def hashPassword(password, salt=None):
    if salt is None:
        salt = os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), hash_rounds)
    return salt, digest.hex()


# make users.txt with the default admin
def seedUsers():
    salt, digest = hashPassword(default_admin[1])
    admin = {"username": default_admin[0], "role": ROLES[0], "salt": salt, "hash": digest}
    saveRecords(USERS_FILE, USER_FIELDS, [admin])


# get all the users, make the admin if the file is missing or empty
def loadUsers():
    if not os.path.exists(filePath(USERS_FILE)):
        seedUsers()
    users = readRecords(USERS_FILE, USER_FIELDS)[0]
    if len(users) == 0:
        seedUsers()
        users = readRecords(USERS_FILE, USER_FIELDS)[0]
    return users


def saveUsers(users):
    return saveRecords(USERS_FILE, USER_FIELDS, users)


# find a user by username
def findUser(users, username):
    for user in users:
        if user["username"].lower() == username.strip().lower():
            return user
    return None


def countAdmins(users):
    count = 0
    for user in users:
        if user["role"] == ROLES[0]:
            count = count + 1
    return count


# check the login, returns (username, role) or None
def login(username, password):
    user = findUser(loadUsers(), username)
    if user is None:
        return None
    try:
        salt, digest = hashPassword(password, user["salt"])
    except ValueError:
        # the salt in the file is broken
        return None
    # same password and salt give the same hash
    if digest == user["hash"]:
        return user["username"], user["role"]
    return None


# password must be 6 or more characters
def checkPassword(password):
    if len(password) < 6:
        return "Password must be at least 6 characters."
    return ""


# add a new user
def registerUser(username, password, role):
    username = username.strip()
    if len(username) < 3 or len(username) > 15 or not username.isalnum():
        return False, "Username must be 3-15 letters or numbers (no spaces)."
    problem = checkPassword(password)
    if problem != "":
        return False, problem
    if role not in ROLES:
        return False, "Invalid role."
    users = loadUsers()
    if findUser(users, username) is not None:
        return False, "That username is already taken."
    salt, digest = hashPassword(password)
    record = {"username": username, "role": role, "salt": salt, "hash": digest}
    if appendRecord(USERS_FILE, USER_FIELDS, record):
        return True, "User " + username + " registered as " + role + "."
    return False, "Could not save the user (file error)."


# change the role of a user, keep at least one admin
def changeRole(username, role):
    users = loadUsers()
    user = findUser(users, username)
    if user is None:
        return False, "User not found."
    if role not in ROLES:
        return False, "Invalid role."
    if user["role"] == ROLES[0] and role != ROLES[0] and countAdmins(users) <= 1:
        return False, "There must be at least one Administrator."
    user["role"] = role
    if saveUsers(users):
        return True, user["username"] + " is now " + role + "."
    return False, "Could not save the changes (file error)."


# set a new password, no old password needed
def resetPassword(username, newPassword):
    problem = checkPassword(newPassword)
    if problem != "":
        return False, problem
    users = loadUsers()
    user = findUser(users, username)
    if user is None:
        return False, "User not found."
    user["salt"], user["hash"] = hashPassword(newPassword)
    if saveUsers(users):
        return True, "Password reset for " + user["username"] + "."
    return False, "Could not save the changes (file error)."


# change your own password, the old one must be right
def changePassword(username, oldPassword, newPassword):
    if login(username, oldPassword) is None:
        return False, "The current password is wrong."
    ok, message = resetPassword(username, newPassword)
    if ok:
        return True, "Your password was updated."
    return False, message


# delete a user, not yourself or the last admin
def deleteUser(username, currentUsername):
    users = loadUsers()
    user = findUser(users, username)
    if user is None:
        return False, "User not found."
    if user["username"].lower() == currentUsername.lower():
        return False, "You cannot delete the account you are using."
    if user["role"] == ROLES[0] and countAdmins(users) <= 1:
        return False, "There must be at least one Administrator."
    users.remove(user)
    if saveUsers(users):
        return True, "User " + user["username"] + " deleted."
    return False, "Could not save the changes (file error)."
