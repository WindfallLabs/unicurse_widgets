# -*- coding: utf-8 -*-
"""
Accela Automation Connection Utility
Author: Garin Wally; Apr 2017

Select a database, login, and select a query to execute.
"""


import os
import re
from getpass import getpass

import pyodbc
import pandas as pd
from unicurses import *


QUERY_DIR = r"I:\00 MAPS\Data\Queries\00 AUTOMATION"
#choices = [q for q in os.listdir(QUERY_DIR) if q.endswith(".sql")]

info_template = "DRIVER={};SERVER={};DATABASE={};UID={};PWD={}"
driver = "{ODBC Driver 13 for SQL Server}"


# Dictionary of database: server
databases = {
    "ACCELA": "CPDBPROD",
    "Test": None
    }

choices = databases.keys()

info = "Use the arrow keys to choose a Database."


# =============================================================================
# RUN

print(__doc__)

# TODO: rm
db = "ACCELA"

# Inputs
user = raw_input("Enter Database Username: ")  # "plangdbo"
pwd = getpass("Password: ")
login = info_template.format(driver, databases[db], db, user, pwd)

info = ("Use the arrow keys to select a query or <ESC> to exit.\n"
        "Database: {}\nUser: {}".format(db, user))

#con = pyodbc.connect(login)

#c = con.cursor()

'''
with open(aa_blic, "r") as f:
    c.execute(f.read())
    r = c.fetchall()
'''



# =============================================================================

WIDTH = 30
HEIGHT = 10
startx = 0
starty = 0

#choices = ["Choice 1", "Choice 2", "Choice 3", "Choice 4", "Exit"]
n_choices = len(choices)

highlight = 1
choice = 0
c = 0

def print_menu(menu_win, highlight):
    x = 2
    y = 2
    box(menu_win, 0, 0)
    for i in range(0, n_choices):
        if (highlight == i + 1):
            wattron(menu_win, A_REVERSE)
            mvwaddstr(menu_win, y, x, choices[i])
            wattroff(menu_win, A_REVERSE)
        else:
            mvwaddstr(menu_win, y, x, choices[i])
        y += 1
    wrefresh(menu_win)

stdscr = initscr()
clear()
noecho()
cbreak()
curs_set(0)
startx = int((80 - WIDTH) / 2)
starty = int((24 - HEIGHT) / 2)

menu_win = newwin(HEIGHT, WIDTH, starty, startx)
keypad(menu_win, True)
mvaddstr(0, 0, info) #"Use arrow keys to go up and down, press ENTER to select a choice")
refresh()
print_menu(menu_win, highlight)

while True:
    c = wgetch(menu_win)
    if c == KEY_UP:
        if highlight == 1:
            highlight == n_choices
        else:
            highlight -= 1
    elif c == KEY_DOWN:
        if highlight == n_choices:
            highlight = 1
        else:
            highlight += 1
    elif c == 10:   # ENTER is pressed
        choice = highlight
        mvaddstr(23, 0, str.format("You chose choice {0} with choice string {1}", choice, choices[choice-1]))
        clrtoeol()
        refresh()
    else:
        mvaddstr(22, 0, str.format("Character pressed is = {0}", c))
        clrtoeol()
        refresh()
    print_menu(menu_win, highlight)
    if c == 27:
        break

refresh()
endwin()
