# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 08:49:08 2017

@author: wallyg
"""

import unicurses as uni


class Menu(object):

    def __init__(self, items, stdscreen):
        self.width = 30
        self.height = 10
        self.startx = int((80 - self.width) / 2)
        self.starty = int((24 - self.height) / 2)
        self.window = uni.newwin(self.height, self.width, self.starty, self.startx)#stdscreen.subwin(0,0)
        #self.window.keypad(1)
        uni.keypad(self.window, True)
        self.panel = uni.new_panel(self.window) #.panel.new_panel(self.window)
        #self.panel.hide()
        #uni.hide_panel(self.panel)
        uni.update_panels()
        #uni.panel.update_panels()

        self.position = 0
        self.items = items
        self.items.append(('exit','exit'))

    def navigate(self, n):
        self.position += n
        if self.position < 0:
            self.position = 0
        elif self.position >= len(self.items):
            self.position = len(self.items)-1

    def display(self):
        #self.panel.top()
        uni.top_panel(self.panel)
        uni.show_panel(self.panel)
        #self.panel.show()
        uni.clear() #self.window.clear()

        while True:
            uni.refresh() #self.window.refresh()
            uni.doupdate()
            for index, item in enumerate(self.items):
                if index == self.position:
                    mode = uni.A_REVERSE
                else:
                    mode = uni.A_NORMAL

                msg = '%d. %s' % (index, item[0])
                uni.mvaddstr(1+index, 1, msg, mode)

            key = uni.getch()

            if key in [uni.KEY_ENTER, ord('\n')]:
                if self.position == len(self.items)-1:
                    break
                else:
                    self.items[self.position][1]()

            elif key == uni.KEY_UP:
                self.navigate(-1)

            elif key == uni.KEY_DOWN:
                self.navigate(1)

        uni.clear() #self.window.clear()
        uni.hide_panel(self.panel)#self.panel.hide()
        uni.update_panels()#panel.update_panels()
        uni.doupdate()

class MyApp(object):

    def __init__(self):#, stdscreen):
        self.screen = uni.initscr() #stdscreen
        uni.keypad(self.screen, True)
        uni.curs_set(0)
        uni.noecho()
        uni.cbreak()
        #menuwin = uni.subwin(self.screen, 23, 79, 0, 0)
        menuwin = uni.newwin(10, 40, 0, 0)
        #uni.box(menuwin, 0, 0)
        #uni.hline(2, 1)#, uni.ACS_HLINE, 77)
        #uni.mvwhline(menuwin, 2, 1, uni.ACS_HLINE, 40 - 2)
        uni.new_panel(menuwin)
        uni.refresh()

        submenu_items = [
                ('beep', uni.beep),
                ('flash', uni.flash)
                ]
        submenu = Menu(submenu_items, self.screen)

        main_menu_items = [
                ('beep', uni.beep),
                ('flash', uni.flash),
                ('submenu', submenu.display)
                ]
        main_menu = Menu(main_menu_items, self.screen)
        main_menu.display()
        #self.main_loop()

    def main_loop(self):
        while True:
            keypress = uni.wgetch(self.screen)
            if keypress == 113:
                break


class Window(object):
    def __init__(self):
        stdscr = uni.initscr()
        uni.start_color()
        uni.cbreak()
        uni.noecho()
        uni.keypad(stdscr, True)

    def add_widget(self, name, widget):
        """mywindow.menubar.add(...)"""
        setattr(self, name, widget)

if __name__ == '__main__':
    try:
        #uni.wrapper(MyApp)
        #stdscr = uni.initscr()
        app = MyApp()
    except Exception as e:
        raw_input(e)