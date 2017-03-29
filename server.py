"""

prompt_toolkit is only used for unix command line interface. It will be removed. You need to run the program from terminal
or else the IDE console will throw a bunch of errors. However it will still work sorta.

Here is the offical asyncio package documentation.
    https://docs.python.org/3/library/asyncio.html
 
This might be useful too, cuz it can be a lot to take in
    http://lucumr.pocoo.org/2016/10/30/i-dont-understand-asyncio/

"""

from __future__ import unicode_literals
import asyncio
import sys
from pickle import loads

from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.interface import CommandLineInterface
from prompt_toolkit.shortcuts import create_prompt_application, create_asyncio_eventloop

from chat_utils import Login, Sender, Request, Message
from chat_utils import toolbar_tokens
from chat_utils import tstamp
from database import Database


# All this stuff, I wouldn't worry about, it's just a shitty command-line interface used for debugging stuff
# =============================== BEGIN NOT WORRYING ===================================================================
cmd_complete = WordCompleter(['/send', '/bye'], ignore_case=True)
sql_completer = WordCompleter(['create', 'select', 'insert', 'drop',
                               'delete', 'from', 'where', 'table'], ignore_case=True)

# This is an asychronous method.
async def server_console(loop):
    history = InMemoryHistory()
    cli = CommandLineInterface(
        application=create_prompt_application('> ',
            completer=cmd_complete,
            history=history,
            get_bottom_toolbar_tokens=toolbar_tokens),
            eventloop=loop)

    sys.stdout = cli.stdout_proxy()     # stdout fd is asynchronous, so print messages as they arrive
    while True:
        try:
            result = await cli.run_async()      # await a command, "await" is an asyncio-specific thing
            for client in clients:              # Maybe you wanna send everyone a message about something
                client.send(result.text)
        except (EOFError, KeyboardInterrupt):
            return
# ================================= END NOT WORRYING ===================================================================

clients = []
cList ={}


"""
This is the server class, which inherits asyncio.Protocol which has 3 main methods:
connection_made()
data_received()
connection_lost()
"""


class Server(asyncio.Protocol):

    db = Database()     # Create a database instance
    db.connect()        # Connect to the database.

    def __init__(self):
        self.transport = None
        self.username = None
        self.addr = None

    def connection_made(self, transport):
        self.transport = transport
        peername = transport.get_extra_info("peername")
        self.username = ""
        self.addr = "{:s}:{:d}".format(*peername)
        print("{0:s}: {1:s} connected".format(tstamp(), self.addr))
        self.send("connected")
        clients.append(self)

    def data_received(self, data):
        data = loads(data)                                          # Unpack that binary data
        print(tstamp() + ' [{}]:'.format(self.username),end='')     # print the data source
        print(" {}\n".format(data))                                 # print the data

        if len(data) == 0:                  # If the size of data is 0, there's nothing, so return
            return

        elif type(data) == Login:             # if data is a Login tuple, send to handler
            self.handle_login(data)

        elif type(data) == Request:           # If data is a Request tuple, send to handler
            self.handle_request(data)

        elif type(data) == Message:           # if data is a Message tuple, send to handler
            self.handle_message(data)

        else:                                 # If message type is not recognized, idk what to do.
            print('Unknown data type, ignoring.')
            return
        
    def connection_lost(self, ex):
        print("{0:s} connection lost: {1:s}".format(tstamp(),self.username) )
        clients.remove(self)
        del cList[self.username]

        # Fix this, only broadcast a user disconnected to someone chatting
        # Right now, message is sent to all clients connected.
        for client in clients:
            client.send("{:s} disconnected".format(self.username))


    # send data through the socket
    def send(self, text, *args):
        # The args is mostly for relaying a message to a recipient and showing the sender's name
        # Otherwise, it just prompts the client that it was a server message
        if args:
            self.transport.write("{0:s} [{1:s}]: {2:s}\n".format(tstamp(),*args, text).encode())
        else:
            self.transport.write("{0:s} [SERVER]: {1:s}\n".format(tstamp(),text).encode())

    # This shouldn't be used right now, its for debugging.
    def send_bin(self,data):
        self.transport.write_object(data)

    def handle_message(self,data):
        cList[data.rcv].send(data.msg,self.username)
        pass
     
    def handle_login(self,data):
        auth = self.db.check_login(data.username, data.pwd)
        self.send("Logged in.\n")
        self.username = data.username
        cList[data.username] = self

    def handle_request(self,data):
        print(data)
        if data.req == "contacts":
            contacts= self.db.query_contact(self.username)
            print("{0:s} [SERVER]: contacts for: {1:}".format(tstamp(),self.username))
            print(*tuple(contacts[i] for i in range(len(contacts))), sep="\n")

            # Get all the contacts, and send them over the socket one at a time
            # This can be done another way in bulk, but it is easier to send them one and display it in terminal
            # on the client side, instead of having the client responsible for formatting the display.
            for c in contacts:
                self.send("{}".format(c))
        
# ===============================================================================

if __name__ == '__main__':
    print("{0:s} [SERVER]: starting.".format(tstamp()))

    loop = asyncio.get_event_loop()

    # Creates the asychronous server, is a generic base class of asynchio
    coroutine = loop.create_server(Server, 'localhost', 9999)
    
    server = loop.run_until_complete(coroutine)

    # If this is kinda confusing look up what "futures" are in python
    # This creates a "future" coroutine for the console. It hasn't been created yet though.
    asyncio.ensure_future(server_console(create_asyncio_eventloop(loop)))

    for socket in server.sockets:
        # Just printing the address and port that it is running on.
        print("{0:s} [SERVER]: running on {1:}".format(tstamp(), socket.getsockname()))

    try:
        loop.run_forever()       # Now run forever, lest you get a keyboard interrupt (ctrl+c)
    except KeyboardInterrupt:
        loop.close()
        print("Bye bye.")
