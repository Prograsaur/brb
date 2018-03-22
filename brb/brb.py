#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Author: Sergey Ishin (Prograsaur) (c) 2018
#-----------------------------------------------------------------------------

'''
Interactive Brokers TWS API -- "The Big Red Button" - one button to cancel all orders and close all positions.

Notes:
TWS API Guide http://interactivebrokers.github.io/tws-api/#gsc.tab=0

To setup the button IB TWS side app:
1) File => Global configuration...
    Configuration => API => Settings
    x Enable ActiveX and Socket Clients
    o Read-Only API
    x Download open orders on connection
    Socket Port: 7497
    x Expose entire trading schedule to API
    x Let API account requests switch user-visible account subscription
    Master API client ID: 0
    x Allow connections from the localhost only
'''

#region import
import sys
import multiprocessing as mp
import queue
import logging

from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order

from config import config
from gui import runGui
from logutils import init_logger
from ibclient import IBClient
#endregion import

class App(IBClient, EWrapper):
    """
    Mixin of Client (message sender and message loop holder)
    and Wrapper (set of callbacks)
    """
    def __init__(self, gui_queue):
        EWrapper.__init__(self)
        IBClient.__init__(self, wrapper=self)

        self.gui_queue = gui_queue
        self.nKeybInt = 0
        self.started = False
        self.brb_active = False
        self._lastId = None

    @property
    def nextId(self):
        self._lastId += 1
        return self._lastId

    def keyboardInterrupt(self):
        """Callback - User pressed Ctrl-C"""
        self.nKeybInt += 1
        if self.nKeybInt == 1:
            msg = "Manual interruption!"
            logging.warn(msg)
            print(msg)
            self._onStop()
        else:
            msg = "Forced Manual interruption!"
            logging.error(msg)
            print(msg)
            self.done = True

    def _onStart(self):
        if self.started: return
        self.started = True
        self.onStart()

    def _onStop(self):
        if not self.started: return
        self.onStop()
        self.started = False

#region GuiMsgProcessors
#----------------------------------------------------------------------------

    def brb(self):
        """
        'The Big Red Button'
        Close all positions, cancel all orders
        """
        if self.brb_active: return
        self.brb_active = True
        self.reqGlobalCancel()
        self.reqPositions()

    def exit(self):
        """
        Exit from the application
        """
        self.done = True
        self._onStop()

#endregion GuiMsgProcessors

#region Callbacks
#----------------------------------------------------------------------------

    def onStart(self):
        logging.info('Main logic started')

    def onStop(self):
        logging.info('Main logic stopped')

    def onLoopIteration(self):
        logging.debug('onLoopIteration()')
        try:
            msg = self.gui_queue.get_nowait()
            logging.info(f'GUI MESSAGE: {msg}')
            if msg == 'BRB':
                self.brb()
            elif msg == 'EXIT':
                self.exit()
            else:
                logging.error(f'Unknown GUI message: {msg}')
        except queue.Empty:
            pass

    def nextValidId(self, orderId: int):
        """
        Callback
        orderId -- First unused order id provided by TWS
        Use reqIds() to request this info
        """
        EWrapper.nextValidId(self, orderId)
        logging.debug(f'Setting next order Id: {orderId}')

        self._lastId = orderId - 1
        self._onStart()

    def position(self, account:str, contract:Contract, position:float,
                 avgCost:float):
        """
        Callback
        This event returns real-time positions for all accounts in
        response to the reqPositions() method.
        """
        EWrapper.position(self, account, contract, position, avgCost)

        # 1. Big Red Button should be in the active mode (Button pressed)
        # 2. Position should be real (avgCost > 0 and position is not 0)
        # 3. Cumulative account 'All' should be skipped
        if self.brb_active and avgCost and position and (account != 'All'):
            order = Order()
            order.orderType = 'MKT'
            order.account = account
            order.totalQuantity = abs(position)
            order.action = ('BUY', 'SELL')[position > 0]
            self.placeOrder(self.nextId, contract, order)

    def positionEnd(self):
        """
        Callback
        End marker for the position() data.
        """
        EWrapper.positionEnd(self)
        self.brb_active = False

#endregion Callbacks

#region main
#-------------------------------------------------------------------------------
def main():
    init_logger('brb', logpath=config.logpath, loglevel=config.loglevel)

    q = mp.Queue()

    # Interactive Brokers TWS API has its own infinite message loop and
    # at least one additional thread.
    # Tkinter from its side “doesn’t like” threads and has an infinite loop as well.
    # To resolve this issue each component will run in the separate process

    gui = mp.Process(target=runGui, args=(q,))
    gui.start()

    logging.info('The Big Red Button started')

    app = App(q)
    app.connect('127.0.0.1', config.twsport, clientId=config.clientId)
    logging.info(f'Server version: {app.serverVersion()}, Connection time: {app.twsConnectionTime()}')
    app.run()

    gui.join()

    logging.info('The Big Red Button stopped')
    return 0

if __name__ == "__main__":
    sys.exit(main())
#endregion main
