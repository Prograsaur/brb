#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Author: Sergey Ishin (Prograsaur) (c) 2018
#-----------------------------------------------------------------------------

'''
Interactive Brokers TWS API -- "The Big Red Button" - one button to cancel all orders and close all positions.

Configuration file
'''

import logging

class Config: pass

config = Config()

config.logpath = 'log'
config.loglevel = logging.INFO
