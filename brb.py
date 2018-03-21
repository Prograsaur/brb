#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Author: Sergey Ishin (Prograsaur) (c) 2018
#-----------------------------------------------------------------------------

'''
Interactive Brokers TWS API -- "The Big Red Button" - one button to cancel all orders and close all positions.
'''

#region import
import sys
import multiprocessing as mp
import queue

from gui import runGui
#endregion import

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
