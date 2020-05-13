#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import tkinter as tk

class Application(tk.Frame):

    def __init__(self, master=None):
        # parameters that you want to send through the Frame class.
        tk.Frame.__init__(self, master)

        #reference to the master widget, which is the tk window
        self.master = master

        # bind event handlers
        self.master.bind('<Key>', lambda a : key_press(a))
        self.master.bind('<Control-q>', ctrl_quit)
        self.master.bind('<Control-w>', lambda a : self.minimize())

        #with that, we want to then run init_window, which doesn't yet exist
        self.init_window()

    def init_window(self):
        # changing the title of our master widget
        self.master.title("PAPER PUBLISHED")

        # screen text to display
        title = tk.Label(self.master, text = "Search for papers that may have been published").place(x=20, y=10)

        # input
        search = tk.Label(self.master, text = "Search").place(x = 30, y = 50)
        searchEntry = tk.Entry(self.master).place(x = 80, y = 50)

        # allowing the widget to take the full space of the root window
        #label.pack(fill=tk.BOTH, expand=1)

        # creating a menu instance
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)

        # create the file object)
        file = tk.Menu(menu) # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit
        file.add_command(label="Exit", command=self.quit)

        #added "file" to our menu
        menu.add_cascade(label="File", menu=file)

        # create the file object
        edit = tk.Menu(menu)

        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit
        edit.add_command(label="Undo")

        #added "file" to our menu
        menu.add_cascade(label="Edit", menu=edit)

    def quit(self):
        exit()

    def minimize(self):
        print("minimize")
        self.master.iconify()

# Event handlers
def key_press(event):
    key = event.char
    print(key, 'is pressed')

def ctrl_quit(event):
    print("Ctrl-Quit event!")
    exit()

def ctrl_w(event):
    print("minimize")
    exit()

if __name__ == "__main__":
    root = tk.Tk()
    # size of the window
    root.geometry("400x300")
    app = Application(root)
    root.mainloop()
