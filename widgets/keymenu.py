# -*- coding: utf-8 -*-

import unicurses as uni

#from uniwidgets import Window

WIDTH = 30
HEIGHT = 10
startx = 0
starty = 0

choices = ["Choice 1", "Choice 2", "Choice 3", "Choice 4", "Exit"]
n_choices = len(choices)

highlight = 1
choice = 0
c = 0

def print_menu(menu_win, highlight):
    x = 2
    y = 2
    uni.box(menu_win, 0, 0)
    for i in range(0, n_choices):
        if (highlight == i + 1):
            uni.wattron(menu_win, uni.A_REVERSE)
            uni.mvwaddstr(menu_win, y, x, choices[i])
            uni.wattroff(menu_win, uni.A_REVERSE)
        else:
            uni.mvwaddstr(menu_win, y, x, choices[i])
        y += 1
    uni.wrefresh(menu_win)

stdscr = uni.initscr()
uni.clear()
uni.noecho()
uni.cbreak()
uni.curs_set(0)
startx = int((80 - WIDTH) / 2)
starty = int((24 - HEIGHT) / 2)

menu_win = uni.newwin(HEIGHT, WIDTH, starty, startx)
uni.keypad(menu_win, True)
uni.mvaddstr(0, 0, "Use arrow keys to go up and down, press ENTER to select a choice")
uni.refresh()
print_menu(menu_win, highlight)

while True:
    keypress = uni.wgetch(menu_win)
    if keypress == uni.KEY_UP:
        if highlight == 1:
            highlight == n_choices
        else:
            highlight -= 1
    elif keypress == uni.KEY_DOWN:
        if highlight == n_choices:
            highlight = 1
        else:
            highlight += 1
    elif keypress in [10, 459]:   # ENTER is pressed
        choice = highlight
        uni.mvaddstr(23, 0, "You chose choice {0} with choice string {1}".format(choice, choices[choice-1]))
        uni.clrtoeol()
        uni.refresh()
    else:
        uni.mvaddstr(22, 0, "Character pressed is = {0}".format(keypress))
        uni.clrtoeol()
        uni.refresh()
    print_menu(menu_win, highlight)
    if choice == 5 or keypress in [27, 113]:
        break

uni.refresh()
uni.endwin()


class Menu(object):
    def __init__(self):
        pass

    def display(self):
        pass




