#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Author: Sergey Ishin (Prograsaur) (c) 2018
#-----------------------------------------------------------------------------

'''
Interactive Brokers TWS API -- "The Big Red Button" - one button to cancel all orders and close all positions.
'''

#region import
import sys
import tkinter as tki
import tkinter.ttk as ttk
import multiprocessing as mp
import queue

import pdb
#endregion import

class Gui:
    def __init__(self, queue):
        self.queue = queue

    def init_gui(self):
        root = self.root = tki.Tk()
        root.title("The Big Red Button")
        root.minsize(240, 240)

        root.iconbitmap('BRB.png.ico')

        self.picture = tki.PhotoImage(file='BRB.png').subsample(3, 3)
        brb = tki.Button(root, image=self.picture, width=64, height=64, bd=0, command=self.on_click_brb)
        brb.grid(row=0, column=0, sticky=tki.NSEW)

        root.columnconfigure(0, weight=1, minsize=124)
        root.rowconfigure(0, weight=1, minsize=176)

        root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def run(self):
        self.init_gui()
        self.root.mainloop()
        
    def on_closing(self):
        from tkinter import messagebox
        if messagebox.askyesno("Quit", "Do you really want to quit?"):
            self.queue.put('EXIT')
            self.root.destroy()

    def on_click_brb(self):
        self.queue.put('BRB')

def runGui(queue):
    gui = Gui(queue)
    gui.run()

#region main
#-------------------------------------------------------------------------------
def main():
    q = mp.Queue()

    gui = mp.Process(target=runGui, args=(q,))
    gui.start()

    active = True
    while active:
        try:
            msg = q.get(True, 0.2)
            if msg == 'EXIT':
                active = False
            elif msg == 'BRB':
                print('BRB!!!')
        except queue.Empty:
            pass
    gui.join()

if __name__ == "__main__":
    sys.exit(main())
#endregion main
