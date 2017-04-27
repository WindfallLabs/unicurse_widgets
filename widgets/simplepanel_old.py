# -*- coding: utf-8 -*-
"""
Unicurses widgets -- wrappers and stuff
"""


import unicurses as uni





QUIT_KEYS = [
    27,  # Esc
    'q', 113,
    'Q', 81
    ]


# Window
NLINES = 10
NCOLS = 40
#my_wins = [0] * 3


stdscr = uni.initscr()
uni.cbreak()
uni.noecho()
uni.keypad(stdscr, True)
uni.curs_set(0)

uni.start_color()






# Sub window
# Max coords of parent window
maxy, maxx = uni.getmaxyx(stdscr)
menu_height = 3
menu = uni.newwin(menu_height, maxx, 0, 0)
starty, startx = uni.getbegyx(menu)
height, width = uni.getmaxyx(menu)


# Box line
uni.box(menu, 0, 0)
#uni.bkgd(uni.COLOR_PAIR(1))

# Box label


#uni.wattron(menu, uni.COLOR_PAIR(0))
#uni.mvwaddstr(menu, 0, 2, "Garin")
uni.mvwaddstr(menu, 1, 1, "File")
uni.mvwaddstr(menu, 1, len("File")+2, "Edit")
#uni.wattroff(menu, uni.COLOR_PAIR(0))
uni.refresh()

#uni.bkgd(uni.COLOR_PAIR(1))

#win_show(my_wins[0], label, 0)


panel = uni.new_panel(menu)
#uni.set_panel_userptr(panel, panel)
uni.update_panels()
uni.doupdate()

while True:
    keypress = uni.getch()
    if keypress == 113:
        break
