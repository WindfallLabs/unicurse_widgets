import unicurses as uni

def win_show(win, label, label_color):
    starty, startx = uni.getbegyx(win)
    height, width = uni.getmaxyx(win)
    uni.box(win, 0, 0)
    uni.mvwaddch(win, 2, 0, uni.ACS_LTEE)
    uni.mvwhline(win, 2, 1, uni.ACS_HLINE, width - 2)
    uni.mvwaddch(win, 2, width - 1, uni.ACS_RTEE)
    print_in_middle(win, 1, 0, width, label, uni.COLOR_PAIR(label_color))

def print_in_middle(win, starty, startx, width, string, color):
    if (win == None): win = stdscr
    y, x = uni.getyx(win)
    if (startx != 0): x = startx
    if (starty != 0): y = starty
    if (width == 0): width = 80
    length = len(string)
    temp = (width - length) / 2
    x = startx + int(temp)
    uni.wattron(win, color)
    uni.mvwaddstr(win, y, x, string)
    uni.wattroff(win, color)
    uni.refresh()

def init_wins(wins, n):
    y = 2
    x = 10
    for i in range(0, n):
        wins[i] = uni.newwin(10, 40, y, x)
        label = str.format("Window number {0}", i + 1)
        win_show(wins[i], label, i + 1)
        y += 3
        x += 7

NLINES = 10
NCOLS = 40
my_wins = [0] * 3
my_panels = [0] * 3

stdscr = uni.initscr()
uni.start_color()
uni.cbreak()
uni.noecho()
uni.keypad(stdscr, True)

uni.init_pair(1, uni.COLOR_RED, uni.COLOR_BLACK)
uni.init_pair(2, uni.COLOR_GREEN, uni.COLOR_BLACK)
uni.init_pair(3, uni.COLOR_BLUE, uni.COLOR_BLACK)
uni.init_pair(4, uni.COLOR_CYAN, uni.COLOR_BLACK)

init_wins(my_wins, 3)

my_panels[0] = uni.new_panel(my_wins[0])
my_panels[1] = uni.new_panel(my_wins[1])
my_panels[2] = uni.new_panel(my_wins[2])

uni.set_panel_userptr(my_panels[0], my_panels[1])
uni.set_panel_userptr(my_panels[1], my_panels[2])
uni.set_panel_userptr(my_panels[2], my_panels[0])

uni.update_panels()

uni.attron(uni.COLOR_PAIR(4))
uni.mvaddstr(0, int(NCOLS / 2) - 2, "Use tab to browse through the windows (Q to Exit)")
uni.attroff(uni.COLOR_PAIR(4))
uni.doupdate()

top = my_panels[2]

ch = -1
while ( (ch != uni.CCHAR('q')) and (ch != uni.CCHAR('Q')) ):
    ch = uni.getch()
    if ch == 9:
        top = uni.panel_userptr(top)
        uni.top_panel(top)
    uni.update_panels()
    uni.doupdate()

uni.endwin()
