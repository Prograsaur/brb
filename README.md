# BRB - "The Big Red Button"
Interactive Brokers TWS API usage example -- one button to cancel all orders and close all positions.

TWS API Guide http://interactivebrokers.github.io/tws-api/#gsc.tab=0

## Usage

1. Configure the TWS (see below)
2. Change ```config.py``` if necessary
2. Run: ```pythonw brb.py```

## Interactive Brokers Trader Workstation configuration

To allow connection between your application and TWS you have to set several options in the TWS configuration:

In the TWS window:
- File => Global configuration...
- Configuration => API => Settings
- [x] Enable ActiveX and Socket Clients
- [ ] Read-Only API
- [x] Download open orders on connection
- Socket Port: 7497
- [x] Expose entire trading schedule to API
- [x] Let API account requests switch user-visible account subscription
- Master API client ID: 0
- [x] Allow connections from the localhost only

## The Big Red Button configuration

Edit config.py file directly to change the configuration.

## Interactive Brokers Client class

Client has to check not just messages from the TWS but messages from the GUI as well.

To do so I just copied the EClient.run() method body from the API code and
added onLoopIteration() hook call inside the EClient infinite loop.

I'm using this hook to process messages from other sources (GUI), not just TWS.

Uncomment self.onIdle() to create another hook to process something while
no messages are comming from the TWS.
