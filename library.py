# Danny Caspary
# CS 361: Software Engineering I
# Main program: Library Catalog

import random
import string
from datetime import *
import time
import zmq
import json
import copy

# keeps track of library members
users = {"sampleID": {
    "password": "stuff",
    "items_out": {"The Way of Zen": date.today() + timedelta(days=-7),
                  "Tomorrow, and Tomorrow, and Tomorrow": date.today() + timedelta(days=2)}
    },
    "2": {
        "password": "stuff",
        "items_out": {}
    }
}

# catalog of works
books = {"The Eye of the World": {
        "author": "Jordan, Robert",
        "status": "available",
        "genre": "Fantasy"
    },
    "Harry Potter and the Prisoner of Azkaban": {
        "author": "Rowling, J.K.",
        "status": "available",
        "genre": "Fantasy"
    },
    "Tomorrow, and Tomorrow, and Tomorrow": {
        "author": "Zevin, Gabrielle",
        "status": "checked out",
        "genre": "Fiction"
    },
    "A Walk in the Woods: Rediscovering America on the Appalachian Trail": {
        "author": "Bryson, Bill",
        "status": "available",
        "genre": "Nonfiction"
    },
    "The Way of Zen": {
        "author": "Watts, Alan",
        "status": "checked out",
        "genre": "Philosophy"
    }
}

genres = ["Fantasy", "Fiction", "Nonfiction", "Philosophy"]
# note: i'm finishing 340 this term too, so
# i'm thinking about transferring these^ to a database over break!
# and, if there's time, switching to a gui


def new_user():
    """registers new library users"""
    # get password from user
    print("First time here? Awesome! Let's get you signed up.")
    pw = input("Please enter a password for your new account: ")

    # generate library id, store data in users dict
    library_id = generate_id()
    users[library_id] = {}
    users[library_id]["password"] = pw
    users[library_id]["items_out"] = {}

    print(f"Excellent! You're all set, your library ID is {library_id}, please keep this for your records!")
    return library_id


def generate_id():
    """
    Generates a random library ID.

    Using function from geeksforgeeks, accessed here:
        https://www.geeksforgeeks.org/generating-random-ids-python/
    """

    # defining function for random string id with parameter
    def ran_gen(size, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for x in range(size))

    # function call for random string
    # generation with size 8 and string
    return ran_gen(8, "AEIOSUMA23")


def login_returning():
    """verifies information for returning library members"""
    library_id = input("Please enter your library ID: ")
    while library_id not in users:
        library_id = input("ID not recognized, please try again: ")
    password = input("Password: ")
    while users[library_id]["password"] != password:
        password = input("Password not recognized, please try again: ")
    print("Welcome back!")

    # use microservice A to check for overdue items
    if users[library_id]["items_out"]:
        time.sleep(1)
        check_for_alert(library_id)
    time.sleep(2)
    return library_id


def check_for_alert(user):
    """runs through checked out books, calls MS_A if needed"""
    items_out = copy.deepcopy(users[user]["items_out"])     # make copy of books to jsonify
    for item, due_date in items_out.items():
        due_date = due_date.day
        days_remaining = get_days_remaining(due_date)
        if days_remaining < 0:
            receive_alert((item, days_remaining))
    receive_alert("Q")


def get_days_remaining(due_date):
    today = date.today()
    today = today.strftime('%d')
    days_remaining = due_date - int(today)
    return days_remaining


def receive_alert(item):
    """
    communicates with msa_send_alert (microservice A) using zeromq
    code adapted from "Introduction to ZeroMQ" by Luis Flores
    """
    context = zmq.Context()                                 # establish zmq connection
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:1738")

    json_item = json.dumps(item)                      # send json items out to MS_A
    socket.send_json(json_item)

    message = socket.recv()                                 # receive alert from MS_A, print
    print(f"{message.decode()}")


def validate_entry(prompt, lower, upper):
    """validate user entry. helper to streamline cli navigation"""
    while True:
        entry = input(prompt)
        if entry.isdigit() and lower <= int(entry) <= upper:
            entry = int(entry)
            return entry
        else:
            print("Invalid entry! Please enter a valid number to continue.")


def library():
    """
    CLI main menu for library operations

    neatly formatted nested dictionary printing sourced from:
        https://stackoverflow.com/questions/15785719/how-to-print-a-dictionary-line-by-line-in-python
    """
    # register new user or login existing
    print("Welcome to the Beaver Library!")
    status = validate_entry("Please enter 1 if you are a new user or 2 if you need to login! ",
                                1, 2)
    if status == 1:
        library_id = new_user()
    else:
        library_id = login_returning()
    print("Just follow the prompts below to view our inventory, search for an item, "
          "or return something you've checked out.")
    time.sleep(4)

    # main menu
    while True:
        print("To view our books, enter 1")
        time.sleep(2)
        print("To look up or check out an item, enter 2")
        time.sleep(2)
        print("To view when your item is due back or return it, enter 3")
        time.sleep(2)
        print("To logout, enter 0")
        time.sleep(4)

        entry = validate_entry("What would you like to do today? Enter a number between 0-3: ", 0, 3)

        if entry == 1:                      # display books
            entry = validate_entry("To view by genre, press 1. To view the entire catalog, press 2:", 1, 2)
            if entry == 1:
                genre_view((genres, books))
                genre_view("Q")
            else:
                for item in books:
                    print(item)
                    for info in books[item]:
                        print(info, ':', books[item][info])

        elif entry == 2:                    # move to item lookup
            item_lookup(library_id)

        elif entry == 3:                    # move to media status if item checked out
            if len(users[library_id]["items_out"]) != 0:
                media_status(library_id)
            else:
                print("It looks like you don't have any items checked out. "
                      "Browse the catalog to find something that catches your eye!")

        else:  # logout
            print("Thanks for stopping by!")
            return


def genre_view(item):
    """
    allows user to view the catalog by genre via Microservice B (MS_B)
    """
    context = zmq.Context()

    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:1739")

    json_item = json.dumps(item)        # send genres and books to MS_B
    socket.send_json(json_item)

    message = socket.recv()                         # receive books by genre from MS_B, print
    print(f"{message.decode()}")


def item_lookup(user):
    """
    Lookup and checkout items in library.

    datetime math sourced from:
        https://stackoverflow.com/questions/6871016/adding-days-to-a-date-in-python
    """
    while True:
        # get valid book title from user
        title = input("Looking for one item in particular? Please enter the title of the item you're looking for: ")
        while title not in books:
            title = input("Title not found, please retry: ")
        print(f"Great choice! It looks like {title} is currently {books[title]['status']}.")

        # if book available, offer to check out
        # else item unavailable, display nav options, may separate into helpers
        if books[title]["status"] == "available":

            entry = validate_entry("Would you like to check this item out? Enter 1 for yes, 2 for no: ", 1, 2)

            if entry == 1:                                                           # check out item
                users[user]["items_out"][title] = date.today() + timedelta(days=14)
                books[title]["status"] = "checked out"
                print(f"Okay! Your book has been checked out. {title} is due back in 14 days.")

                entry = validate_entry("Press 1 to look up another book or"   # offer quick exit after checkout
                                       " press 2 to return to the homepage:", 1, 2)
                if entry == 1:
                    continue
                return

            elif entry == 2:                                                          # user declined to check out
                entry = input("Okay, great. Is there something else you'd like to look at? Enter 1 for yes, 2 for no: ")
                if entry == 1:
                    continue
                return

        else:                                                                          # item unavailable
            print("We will notify you when it is back in stock!")
            entry = validate_entry("Would you like to look at another item? "
                                   "Press 1 for yes or 2 to return to the homepage.", 1, 2)
            if entry == 1:
                continue
            return


def media_status(user):
    """
    Shows user how many items they have checked out, their return dates, and allows users to return said items.
    days_remaining calculation used from this SO thread:
        https://stackoverflow.com/questions/7628036/how-much-days-left-from-today-to-given-date
    """
    items_out = users[user]["items_out"]
    num_items_out = len(users[user]['items_out'])
    print(f"Let's see here...it looks like you have {num_items_out} item(s) currently checked out!")

    # print days remaining for each book user has checked out, might pull into helper
    for item, due_date in items_out.items():
        today = date.today()
        days_remaining = due_date - today
        print(f"Your copy of {item} is due back in {days_remaining.days} days. Thank you for staying on top of it!")

    # user nav
    while True:
        entry = validate_entry("Would you like to return an item today? "
                               "Please enter 1 for yes, or 2 to return to the homepage:", 1, 2)
        if entry == 1:
            item_for_return = input("Please enter the title of the item you'd like to return:")
            if item_for_return in items_out:
                if return_book(items_out, num_items_out, item_for_return):
                    num_items_out = len(users[user]['items_out'])
                    continue
                return
            print("Sorry we don't have that title on file for you. Please try again.")
        elif entry == 2:
            return


def return_book(items_out, num_items_out, item_for_return):
    """returns a book, helper for media status to clean up conditionals"""
    entry = validate_entry("Are you sure you'd like to return this item? "
                           "This action cannot be undone (Enter 1 for yes, 2 for no): ", 1, 2)
    if entry == 1:
        del items_out[item_for_return]      # return item
        books[item_for_return]["status"] = "available"
        num_items_out -= 1
        if another_return(num_items_out):
            return True
        return False

    print("Okay! No sweat.")                # user declined return
    if another_return(num_items_out):
        return True
    return False


def another_return(num_items_out):
    """helper for media_status and return_book, cleans up nested if else hell from CLI navigation"""
    if num_items_out > 0:
        entry = validate_entry("To return another item, press 1. "
                               "To go back to the homepage, press 2: ", 1, 2)
        if entry == 1:
            return True
        return False
    else:
        print("You don't have any more items checked out, so we will bring you back to the homepage!")
        return False


library()
