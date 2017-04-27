# -*- coding: utf-8 -*-
"""
Unicurses widgets -- wrappers and stuff
Author: Garin Wally; Apr 2017

This module acts as an expansion to unicurses which provides high-level
widgets and wrappers.
"""

import time
import sys
import webbrowser
from collections import OrderedDict, Container, deque

import unicurses as uni


__all__ = ["SizeError", "Window", "Widget", "Menubar", "Box", "Textbox"]


# Errors
class SizeError(Exception):
    pass


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


# =============================================================================
# WIDGETS & OBJECTS

class Click(object):
    """Mouse click object."""
    def __init__(self):
        self.id, self.x, self.y, self.z, self.bstate = uni.getmouse()
        self.is_clicked = False
        if self.bstate & uni.BUTTON1_PRESSED:
            self.is_clicked = True
        self.debug = "Click: {0}, {1}, {2}".format(self.x, self.y, self.z)

    @property
    def coords(self):  # TODO: are these coords correct?
        return (self.x, self.y)


class Widget(object):
    """Base class for unicurses widgets."""
    def __init__(self, window):
        # Parent window
        self._parent = window
        # Widget window
        self.win = None
        self.height = 0
        self.width = 0
        self.label_indent = 2

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

    def draw_label(self):
        """Draws widget label."""
        if not hasattr(self, "label"):
            raise AttributeError("Widget has no attribute 'label'")
        if (len(self.label) + 2) >= self.width:
            raise SizeError("Label is longer than box.")
        # TODO: label styles
        # if self.label_color_pair > 0:
        # uni.wattron(self.boxwin, uni.COLOR_PAIR(self.label_color_pair))
        uni.mvwaddstr(self.win, 0, self.label_indent, self.label)
        # if self.label_color_pair > 0:
        #    uni.wattroff(self.boxwin, uni.COLOR_PAIR(self.label_color_pair))


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
        # Enable mouse
        uni.mouseinterval(0)
        uni.mousemask(uni.ALL_MOUSE_EVENTS)
        # Window dimensions
        y, x = uni.getmaxyx(self.stdscr)
        # Make maxx/maxy the last row/col visible
        self.maxy = y - 1
        self.maxx = x - 1
        # Drawing order of contained widgets
        self.widgets = []

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
        sys.exit(0)

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
    def __init__(self, window, xpos, ypos, height, width, label="",
                 outline=True, label_color_pair=0):
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
        self.draw_label()

        # Box fill
        # TODO: color fill

        # Write contents in order
        for line in self.content:
            ix = self.content.index(line) + 2
            uni.mvwaddstr(self.win, ix, 2, line)

        # Only create panel attribute on display
        self.panel = uni.new_panel(self.win)

    def add_content(self, text):
        self.content.append(text)

    def fit_to_content(self):
        max_content = max([len(c) for c in self.content])
        label_len = len(self.label)
        self.width = max([max_content, label_len]) + 4
        self.height = len(self.content) + 4


class _SubmenuOption(object):
    def __init__(self, name, action, args=()):
        self.name = name
        self.action = action
        self.args = args


class _Submenu(object):
    def __init__(self, name, options):
        self.name = name
        self.options = options
        # {"Exit": (win.destroy, "Later dude")}
        # 'e': {"action": options[0], "args": options[1]}

        # Calculated by Menubar
        self.xpos = 0

        # Set initial key
        self.key = self.name[0].lower()

        # Actions dict (e.g. self.actions[e] -> win.destroy ("Exit"))
        self.actions = {}
        #self.option_keys = {}
        for option in self.options:
            ix = 0
            f_letter = ord(option[ix].lower())
            while f_letter in self.actions.keys():#self.option_keys.keys():
                ix += 1
                f_letter = ord(option[ix].lower())
            # Default action and args
            action = None
            args = ()
            # Handle single function/method or None
            pot_action = self.options[option]
            if pot_action is None:
                pass
            elif pot_action is not None and hasattr(pot_action, "__call__"):
                action = pot_action
            elif len(pot_action) > 1 and hasattr(pot_action[0], "__call__"):
                action = pot_action[0]
                if pot_action[1]:
                    args = pot_action[1]
            self.actions[f_letter] = {"action": action,
                                      "args": args}

    @property
    def bounds(self):
        """Bounding box of the object for click-target."""
        return (range(self.xpos, len(self.name)), 1)

    def action(self, key):
        """Execute an option's action."""
        action = self.actions[key]["action"]
        args = self.actions[key]["args"]
        # Handle None
        if not hasattr(action, "__call__"):
            return
        if args:
            action(args)
            return
        action()
        return


class Menubar(Widget):
    """Horizontal menubar (File, Edit, Help, etc)."""
    def __init__(self, window, label="", label_color_pair=0):
        super(Menubar, self).__init__(window)
        self.label = label
        self.label_color_pair = label_color_pair
        self.height = 3
        self.width = self._parent.maxx
        #self.sections = OrderedDict()
        self.submenus = []
        self.selection = None
        # Start window at (0, 0); span 3 down and entire width over
        self.win = uni.newwin(self.height, self.width, 0, 0)

    def render(self):
        """Show the menubar."""
        #self.make_panels()
        # Box line
        uni.box(self.win, 0, 0)
        # Label
        self.draw_label()

        uni.doupdate()
        self.panel = uni.new_panel(self.win)
        uni.panel_above(self.panel)

        # Print submenu names
        self.update_section_atts()
        self.make_panels()
        for submenu in self.submenus:
            uni.mvwaddstr(self.win, 1, submenu.xpos, submenu.name)
            # TODO: highlight selected submenu/options

    def update_section_atts(self):
        """Calculates spacing between sections."""
        if self.submenus:
            xpos = 2
            for submenu in self.submenus:
                submenu.xpos = xpos
                xpos += len(submenu.name) + 2

    @property
    def menukeys(self):
        """Key for each menubar submenu."""
        return {ord(submenu.key): submenu for submenu in self.submenus}

    def make_panels(self):
        """Dict of submenus by submenu name."""
        for submenu in self.submenus:
            box = Box(self._parent, submenu.xpos, 2, 20, 20)
            box.label_indent = 1
            for option in submenu.options:
                box.add_content(option)
            box.fit_to_content()
            submenu.panel = box

    def add_submenu(self, name, options):
        """Add submenu to menubar (e.g. File, Edit, etc.)."""
        new_submenu = _Submenu(name, options)
        self.submenus.append(new_submenu)

    def show_submenu(self, key):
        self.open_submenu = self.menukeys[key]
        self.selection = self.open_submenu.panel
        self.selection.show()
        uni.update_panels()

        # Listen for keypress with submenu open
        while True:
            c = uni.wgetch(self.win)
            if c in QUIT_KEYS:
                self.reset()
                break
            elif c in self.open_submenu.actions: # option_keys
                uni.mvaddstr(win.maxy, 0,
                             "DEBUG: Character pressed: {0}".format(c))
                uni.refresh()
                self.open_submenu.action(c)

    def reset(self):
        if self.selection:
            self.selection.hide()
        uni.update_panels()
        uni.refresh()


class Textbox(Box):  # TODO: deque and scroll modes / subclasses
    def __init__(self, window, xpos, ypos, height, width, label="",
                 outline=True, xpad=0, ypad=0, label_color_pair=0):
        super(Textbox, self).__init__(
            window, xpos, ypos, height, width, label=label,
            outline=outline, label_color_pair=label_color_pair)

        # Padding (i.e. spaces between text and border (+1))
        self.ypad = ypad + 1
        self.xpad = xpad + 1

        # Text content, ordered by list index
        self.all_lines = []

        # Size rules
        self.min_height = 3
        # Textbox can only have a max height of the parent window's height
        win_max_y = self._parent.maxy - 3
        if self.height > win_max_y:
            self.height = win_max_y
        # Textbox can only have a max width of the parent window's width
        win_max_x = self._parent.maxx
        if self.width > win_max_x:
            self.width = win_max_x
        # Textbox must be at least 3 tall
        if self.height < self.min_height:
            self.height = 3
        # TODO: xpos and ypos limits
        # Errors are raised if textbox is smaller than content or label

    @property
    def lines(self):
        return deque(self.all_lines, self.height - 2)

    @property
    def max_line_len(self):
        return max([len(line) for line in self.all_lines])

    def add_line(self, text, line=None):
        if line is None:
            self.all_lines.append(text)
        else:
            self.all_lines.insert(line, text)

    def render(self, line=None):  # Overwrites existing
        if self.max_line_len > self.width:
            raise SizeError("Content is longer than box.")
        # New window
        self.win = uni.newwin(self.height, self.width, self.ypos, self.xpos)

        # Draw outline
        if self.outline:
            uni.box(self.win, 0, 0)
        # Draw label
        self.draw_label()

        # Make panel
        self.panel = uni.new_panel(self.win)

        # Track the line number currently written
        self.current_line = 0

        # Print content
        for line in self.lines:
            # Print line text on line number
            ix = list(self.lines).index(line)
            line_no = ix + self.ypad
            # Print lines according to the text's index in the list
            uni.mvwaddstr(self.win, line_no, self.xpad, " "*(self.width-2))
            uni.mvwaddstr(self.win, line_no, self.xpad, line)
            self.current_line += 1
            uni.wrefresh(self.win)


if __name__ == "__main__":
    try:
        win = Window()

        # Create menubar
        menu = Menubar(win)
        #menu.add_section("File", [["New", 1], ["Open", 2],
        #                          ["Recent", 3], ["Exit", 4]])
        #menu.add_section("Edit", [["Remove", None]])
        #menu.add_section("Options", [["Preferences", None]])
        #menu.add_section("Help", [["About", "Garin"], ["Website", "www..."]])
        menu.add_submenu("File", {"New": None,
                                  "Open": None,
                                  "Nonsense": None,
                                  "Exit": win.destroy})
        menu.add_submenu("Edit", {"Undo": None,
                                  "Redo": None,
                                  "Reduce": None})
        menu.add_submenu("Options", {"Preferences": None})
        menu.add_submenu("Help", {"About": None,
                                  "Web": (webbrowser.open, "https://github.com/WindfallLabs/unicurse_widgets")})

        # Add menubar to window's drawing order
        win.add_widget("menu", menu)

        textbox = Textbox(win, 0, 3, 5, win.maxx/2, label="<Clicks>")
        # TODO: raise drawing error when win.maxy, 3
        textbox.add_line("Start")
        textbox.add_line("clicking")
        win.add_widget("textbox", textbox)

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
                click = Click()
                if click.is_clicked:
                    textbox.add_line(str(click.coords))
                    uni.mvaddstr(win.maxy, 0, "DEBUG: {0}".format(click.debug))

            if c != 539:
                uni.mvaddstr(win.maxy, 0,
                             "DEBUG: Character pressed: {0}".format(c))
            uni.refresh()

    except Exception as e:
        raw_input(e)

    finally:
        # Quit
        win.destroy("Goodbye")
