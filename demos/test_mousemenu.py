import unicurses as uni

WIDTH = 30
HEIGHT = 10
startx = 0
starty = 0

choices = ["Choice 1", "Choice 2", "Choice 3", "Choice 4", "Exit"]
n_choices = len(choices)

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

def report_choice(mouse_x, mouse_y):
    i = startx + 2
    j = starty + 3
    for choice in range(0, n_choices):
        if (mouse_y == j + choice) and (mouse_x >= i) and (mouse_x <= i + len(choices[choice])):
            if choice == n_choices - 1:
                return -1
            else:
                return choice + 1
            break

stdscr = uni.initscr()
uni.clear()
uni.noecho()
uni.cbreak()
uni.curs_set(0)
startx = int((80 - WIDTH) / 2)
starty = int((24 - HEIGHT) / 2)

menu_win = uni.newwin(HEIGHT, WIDTH, starty, startx)
uni.keypad(menu_win, True)
uni.mvaddstr(0, 0, "Click on Exit to quit (works best in a virtual console)")
uni.refresh()
print_menu(menu_win, 1)
uni.mouseinterval(0)
uni.mousemask(uni.ALL_MOUSE_EVENTS)


msg = "MOUSE: {0}, {1}, {2}, Choice made is: {3}, Chosen string is: {4}"
while True:
    c = uni.wgetch(menu_win)
    if c == uni.KEY_MOUSE:
        id, x, y, z, bstate = uni.getmouse()
        if bstate & uni.BUTTON1_PRESSED:
            chosen = report_choice(x + 1, y + 1)
            if chosen is not None:
                uni.mvaddstr(23, 0, msg.format(
                    x, y, bstate, chosen, choices[chosen-1]))
                uni.mvaddstr(23, 0, msg.format(
                    x, y, bstate, chosen, choices[chosen-1]))
            uni.clrtoeol()
            uni.refresh()
            if (chosen == -1):
                uni.endwin()
                exit(1)
            print_menu(menu_win, chosen)

uni.endwin()
