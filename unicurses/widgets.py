import time
from unicurses import *

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

def title(string, line=0):
    mvaddstr(line, 0, string)
    mvchgat(line, 0, -1, A_REVERSE, 1, None)

def mainloop(f=None):
    ch = -1
    while ( (ch != CCHAR("q")) and (ch != CCHAR('Q')) ):
        ch = getch()
        if f:
            f(ch)
    


'''
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
    if choice == 5:
        break
'''

if __name__ == "__main__":
    stdscr = initscr()
    clear()
    noecho()
    cbreak()
    curs_set(0)
    startx = int((80 - WIDTH) / 2)
    starty = int((24 - HEIGHT) / 2)
    maxy = getmaxyx(stdscr)[0] - 1
    #maxx = getmaxys(stdscr)[1] - 1

    menu_win = newwin(HEIGHT, WIDTH, starty, startx)
    keypad(menu_win, True)
    title("Garin is awesome")
    title("Last line", line=maxy-1)

    refresh()
    @mainloop
    def do(ch=-1):
        if ch == CCHAR('g'):
            title("New title line!")

    do()

    refresh()
    endwin()
