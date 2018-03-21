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
import logging

from gui import runGui
from logutils import init_logger
from config import config
#endregion import

#region main
#-------------------------------------------------------------------------------
def main():
    init_logger('brb', logpath=config.logpath, loglevel=config.loglevel)

    q = mp.Queue()

    # Interactive Brokers TWS API has its own infinite message loop and
    # at least one additional thread.
    # Tkinter from its side “doesn’t like” treads and has infinite loop too.
    #
    # To resolve this issue each component will run in the separate process:
    gui = mp.Process(target=runGui, args=(q,))
    gui.start()

    logging.info('The Big Red Button started')

    active = True
    while active:
        try:
            msg = q.get(True, 0.2)
            logging.debug(f'Message from GUI: {msg}')
            if msg == 'EXIT':
                active = False
            elif msg == 'BRB':
                print('BRB!!!')
        except queue.Empty:
            pass
    gui.join()
    logging.info('The Big Red Button stopped')

    return 0

if __name__ == "__main__":
    sys.exit(main())
#endregion main
