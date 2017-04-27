# -*- coding: utf-8 -*-
"""
Unicurses widgets -- wrappers and stuff
Author: Garin Wally; Apr 2017

This module acts as an expansion to unicurses which provides high-level
widgets and wrappers.
"""

import time
from collections import OrderedDict, Container

import unicurses as uni


# Dict of colors
colors = {
    "black": uni.COLOR_BLACK,
    "blue": uni.COLOR_BLUE,
    "cyan": uni.COLOR_CYAN,
    "green": uni.COLOR_GREEN,
    "magenta": uni.COLOR_MAGENTA,
    "red": uni.COLOR_RED,
    "white": uni.COLOR_WHITE,
    "yello": uni.COLOR_YELLOW
    }


# Color pairs
uni.init_pair(0, uni.COLOR_WHITE, uni.COLOR_BLACK)
uni.init_pair(1, uni.COLOR_BLACK, uni.COLOR_WHITE)
uni.init_pair(2, uni.COLOR_CYAN, uni.COLOR_BLUE)
uni.init_pair(3, uni.COLOR_GREEN, uni.COLOR_BLACK)
'''
# Named color pairs
color_schemes = {
    "normal": uni.COLOR_PAIR(0),
    "inverse": uni.COLOR_PAIR(1),
    "cyan": uni.COLOR_PAIR(2),
    "green": uni.COLOR_PAIR(3)
    }
'''

YES_KEYS = [
    "y", 121,
    "Y", 89
    ]

QUIT_KEYS = [
    'q', 113,
    'Q', 81,
    27  # Esc
    ]


def write(scrid, text, ypos, xpos, color="white"):
    uni.setsyx(ypos, xpos)
    uni.waddstr(scrid, text)
    uni.setsyx(0, 0)
    uni.refresh()
    uni.update_panels()
    uni.doupdate()


class Widget(object):
    """Base class for unicurses widgets."""
    def __init__(self, window):
        # Parent window
        self._parent = window
        # Widget window
        self.win = None

    def show(self, render_fn=None):
        """Show the widget."""
        # Call render() method if exists
        if hasattr(self, "render"):
            self.render()
        if hasattr(self, "panel"):
            uni.show_panel(self.panel)
        uni.update_panels()

    def hide(self):
        """Hide the widget."""
        uni.hide_panel(self.panel)
        uni.update_panels()


class Window(object):
    """Parent window object."""
    def __init__(self):
        # Initialize screen
        self.stdscr = uni.initscr()
        # Hide cursor
        uni.curs_set(0)
        # Characters available one-by-one
        uni.cbreak()
        # Prevent displying user input
        uni.noecho()
        # Allow user input
        uni.keypad(self.stdscr, True)
        # Enable colors
        uni.start_color()
        # Window dimensions
        self.maxy, self.maxx = uni.getmaxyx(self.stdscr)
        # Drawing order of contained widgets
        self.widgets = []
        # Track keypresses
        #self.keypress = -1

    def get_drawing_order(self):
        """Displays the child widgets and index in drawing order."""
        return [(w, self.widgets.index(w)) for w in self.widgets]

    def reset(self):
        """Clears the window and sets cursor to (0, 0)."""
        uni.setsyx(0, 0)
        uni.erase()
        uni.refresh()

    def destroy(self, msg="", wait=2):
        """Clears and closes the window with optional message."""
        # Reset cursor position
        if msg:
            self.reset()
            uni.addstr(msg)
            uni.refresh()
            time.sleep(wait)
        uni.endwin()

    def add_widget(self, name, widget):
        """Add widget object to window's drawing order."""
        # Add widget (child) to window (parent) as object and list item
        setattr(self, name, widget)
        self.widgets.append(widget)

    def enable_colors(self):
        """Turns terminal colors on."""
        uni.start_color()

    def draw(self):
        """Draw window and all child widgets."""
        uni.clrtobot()
        uni.refresh()
        # Requires all child widgets to have a show method
        [w.show() for w in self.widgets]
        uni.update_panels()
        uni.doupdate()


class Box(Widget):
    def __init__(self, window, xpos, ypos, height, width, label="", outline=True, label_color_pair=0):
        super(Box, self).__init__(window)
        self.label = label
        self.label_color_pair = label_color_pair
        self.outline = outline
        self.xpos = xpos
        self.ypos = ypos
        self.height = height
        self.width = width
        self.content = []

    def render(self):
        """Renders but does not show the widget."""
        # Draw the box line
        self.win = uni.newwin(self.height, self.width, self.ypos, self.xpos)
        if self.outline:
            uni.box(self.win, 0, 0)

        # Label
        if (len(self.label) + 2) > self.width:
            raise AttributeError("Label is longer than box.")
        #if self.label_color_pair > 0:
        #uni.wattron(self.boxwin, color_schemes["cyan"])
        uni.mvwaddstr(self.win, 0, 2, self.label)
        #if self.label_color_pair > 0:
        #    uni.wattroff(self.boxwin, uni.COLOR_PAIR(self.label_color_pair))

        # Box fill
        # TODO: color fill

        # Write contents in order
        for line in self.content:
            ix = self.content.index(line) + 2
            uni.mvwaddstr(self.win, ix, 2, line[0])

        # Only create panel attribute on display
        self.panel = uni.new_panel(self.win)

    def add_content(self, text):
        self.content.append(text)

    def fit_to_content(self):
        max_content = max([len(c[0]) for c in self.content])
        label_len = len(self.label)
        self.width = max([max_content, label_len]) + 4
        self.height = len(self.content) + 4


class _MenuSection(object):
    def __init__(self, parent, name, contents):
        self.parent_menu = parent
        self.name = name
        self.contents = contents
        # Set initial key
        self.key = self.name[0]
        # Set bounding box of section
        # TODO: x, y
        self.bounds = (range(0, 0), 0)

    @property
    def ix(self):
        return self.parent_menu.sections.index(self.name)  # TODO: menubar.sections must be list


class Menubar(Widget):
    """Horizontal menubar (File, Edit, Help, etc)."""
    def __init__(self, window, label="", label_color_pair=0):
        super(Menubar, self).__init__(window)
        self._parent = window
        self.label = label
        self.label_color_pair = label_color_pair
        self.sections = OrderedDict()  # TODO: make list, make sections objects
        self.selection = None
        # Start window at (0, 0); span 3 down and entire width over
        self.win = uni.newwin(3, self._parent.maxx, 0, 0)

    def render(self):
        """Show the menubar."""
        self.make_panels()
        # Box line
        uni.box(self.win, 0, 0)
        # Label
        if self.label_color_pair > 0:
            uni.wattron(self.win, uni.COLOR_PAIR(self.label_color_pair))
        uni.mvwaddstr(self.win, 0, 2, self.label)
        if self.label_color_pair > 0:
            uni.wattroff(self.win, uni.COLOR_PAIR(self.label_color_pair))
        uni.doupdate()
        self.panel = uni.new_panel(self.win)
        uni.panel_above(self.panel)

        # Sections
        for section in self.sections:
            uni.mvwaddstr(self.win, 1, self.section_ix[section], section)

    @property
    def section_ix(self):
        """Calculates spacing between sections."""
        ixs = {}
        if self.sections:
            spaces = 2
            for k in self.sections.keys():
                ixs[k] = spaces
                spaces += len(k) + 2
        return ixs

    @property
    def menukeys(self):
        """Key for each menubar section."""
        return {ord(k.lower()[0]): self.panels[k] for k in self.sections.keys()}

    def make_panels(self):
        """Dict of submenus by section name."""
        panels = {}
        for section in self.sections:
            box = Box(self._parent, self.section_ix[section]-1, 1,
                      20, 20, "<{}>".format(section))
            for opt in self.sections[section]:
                box.add_content(opt)
            box.fit_to_content()
            panels[section] = box
        self.panels = panels

    def add_section(self, name, contents=[]):
        """Add header/section to menubar (e.g. File, Edit, etc.)."""
        if isinstance(contents, Container) and not isinstance(contents, str):
            self.sections[name] = contents

    def show_submenu(self, key):
        self.selection = self.menukeys[key]
        self.selection.show()
        uni.panel_above(self.selection.panel)
        uni.update_panels()
        # Listen for keypress with submenu open
        while True:
            c = uni.wgetch(self.win)
            if c in QUIT_KEYS:
                self.reset()
                break

    def reset(self):
        if self.selection:
            self.selection.hide()
        uni.update_panels()
        uni.refresh()


class Textbox(Box):
    def __init__(self, window, xpos, ypos, height, width, label="", outline=True, label_color_pair=0):
        super(Textbox, self).__init__(
            window, xpos, ypos, height, width, label=label,
            outline=outline, label_color_pair=label_color_pair)
        # Inside margins
        #self.ymargin = ypos + 1
        #self.xmargin = xpos + 1
        self.indent = 2
        #self.current_line = self.ymargin + 1
        self.lines = []

    def add_line(self, text, line=None):
        if line is None:
            self.lines.append(text)
        else:
            self.lines.insert(line, text)

    def render(self, line=None):  # Overwrites existing
        # New window
        self.win = uni.newwin(self.height, self.width, self.ypos, self.xpos)
        # Draw outline
        if self.outline:
            uni.box(self.win, 0, 0)
        # Draw label
        if self.label:
            uni.mvwaddstr(self.win, 0, 2, self.label)
        # Make panel
        self.panel = uni.new_panel(self.win)

        # Print content
        for line in self.lines:
            uni.mvwaddstr(self.win, self.lines.index(line) + 2,
                          self.indent, line)
        uni.refresh()


class Click(object):
    """Mouse click object."""
    def __init__(self, debug=False):
        self.id, self.x, self.y, self.z, self.bstate = uni.getmouse()
        self.is_clicked = False
        if self.bstate & uni.BUTTON1_PRESSED:
            self.is_clicked = True

    @property
    def coords(self):  # TODO: are these coords correct?
        return (self.x, self.y)


if __name__ == "__main__":
    try:
        win = Window()
        uni.mouseinterval(0)
        uni.mousemask(uni.ALL_MOUSE_EVENTS)
        # Create menubar
        menu = Menubar(win)
        menu.add_section("File", [["New", 1], ["Open", 2],
                                  ["Recent", 3], ["Exit", 4]])
        menu.add_section("Edit", [["Remove", None]])
        menu.add_section("Options", [["Preferences", None]])
        menu.add_section("Help", [["About", "Garin"], ["Website", "www..."]])
        # Add menubar to window's drawing order

        # TODO: set H & W where
        textbox = Textbox(win, 0, 3, 0, 0, label="<Messages>")
        textbox.add_line("Garin")
        textbox.add_line("is")
        textbox.add_line("Awesome!")
        win.add_widget("textbox", textbox)
        win.add_widget("menu", menu)

        # Main loop
        while True:
            # Draw window and child widgets
            win.draw()

            # Get keys
            c = uni.getch()

            # Quit
            if c in QUIT_KEYS:
                break

            # Open submenus with corresponding key
            if c in menu.menukeys.keys():
                # Clear any opened menus
                menu.reset()

                # Show submenu by keypress
                menu.show_submenu(c)

            if c == uni.KEY_MOUSE:
                click = Click(True)
                if click.is_clicked:
                    textbox.add_line(str(click.coords))


            uni.mvaddstr(23, 0, "DEBUG: Character pressed: {0}".format(c))
            uni.refresh()



    except Exception as e:
        raw_input(e)

    finally:
        # Quit
        win.destroy("Goodbye")
