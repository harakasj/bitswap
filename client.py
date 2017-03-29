"""
Using asyncio from python, we can asynchronously send and receive data from the server we connect to instead of 
creating a listener thread to check for incoming data. This is much more efficient because the thread blocks every time
it polls for incoming data. 

Instead, make the client connection a coroutine, so its not just an idling thread. 

Communication is handled using named tuples. 
These tuples are pickled and sent through the socket as binaries.
The server receives the binary file and unpacks it. 
The server checks to see what kind of tuple it is.
Depending on the type, the server calls the appropriate action.

For example, to login, the username and password are sent as the following named tuple:
    Login = namedtuple("Login", "username pwd")
When
    user = 'paddlingcharlie'
    pwd = 'my_pass123'
    login_info = Login(user,pwd)
    client.send(login_info)
    
When the client.send(login_info) is called, it packs the binary and writes it to the transport method of the tcp client.
    login_info_binary = pickle.dumps(login_info)
    transport.write( login_info_binary )
    
When data is received by the server (or client), it is passed to data_receieved(some_data)
    data = pickle.loads( some_data)

Where the server reads the binary data using pickle.loads()
Then the server compares the type of the data:

    if type(data) == Login:
        handle_login(data)
        
Since the data type is a named tuple Login, send it to the right area:

    handle_login(data)
    
The nice thing about named tuples is that you can reference the fields:

    database.check_login(data.username, data.pwd)
    
where you lookup the username and password fields by calling database.check_login(data.username, data.pwd) 
The query returns true or false depending on if the login information is found. 
     
"""

from __future__ import unicode_literals

import asyncio
import sys
from pickle import dumps

# All prompt_toolkit imports are for linux curses, a simple command line interface. This will be removed soon.
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.interface import CommandLineInterface
from prompt_toolkit.shortcuts import create_prompt_application, create_asyncio_eventloop, prompt_async


# These are some imports specific to the client-server.
from chat_utils import Login, Sender, Request, Message      # import the tuples that we use for communication
from chat_utils import toolbar_tokens
from chat_utils import tstamp

loop = asyncio.get_event_loop()
client = []
cmd_complete = WordCompleter(['send', 'bye', 'contacts'], match_middle=True, ignore_case=True)


async def client_talk(loop):
    usr = await prompt_async("username:", eventloop=loop, patch_stdout=True)
    pwd = await prompt_async("password:", eventloop=loop, patch_stdout=True, is_password=True)
    cin = usr + ">"
    contacts = []
    history = InMemoryHistory()
    cli = CommandLineInterface(
        application=create_prompt_application(
        cin, history=history,
        completer=cmd_complete,
        get_bottom_toolbar_tokens=toolbar_tokens),
        eventloop=loop
    )

    sys.stdout = cli.stdout_proxy()
    client[0].send(Login(usr, pwd))
    cin = usr + ">"

    while True:
        try:
            msg = await cli.run_async()
            msg = msg.text
            try:
                if msg.startswith("/"):
                    msg = msg.split(sep="/")
                    if msg[1] == "bye":
                        client[0].close_conn()

                    elif msg[1] == "contacts":
                        client[0].send(Request("contacts", usr))

                    elif msg[1] == "send":
                        client[0].send(Message(msg[2], msg[3]))
                        print("{0:s} [{1:s}]: {2:s}\n".format(tstamp(), usr, msg[3]))
                    else:
                        raise IndexError
            except IndexError:
                print("Not understood.")
                continue

        except (EOFError, KeyboardInterrupt):
            return


class Client(asyncio.Protocol):
    def __init__(self):
        self.loop = loop
        self.transport = None
        client.append(self)

    def connection_made(self, transport):
        print('CONNECT')
        self.transport = transport

    def data_received(self, data):
        print('{}'.format(data.decode('utf-8')))

    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop the event loop')
        self.loop.stop()

    def close_conn(self):
        self.loop.stop()

    # sends pickled data
    def send(self, data):
        self.transport.write(dumps(data))


def main():
    # Create an asynchronous event loop.
    loop = asyncio.get_event_loop()

    try:
        # We are creating a coroutine - a tcp client
        couroutine = loop.create_connection(Client, 'localhost', 9999)
        loop.run_until_complete(couroutine)

        # setting a future allows you to declare something that hasn't been called yet.
        # So we set a client which will get called down the line, but not yet.
        asyncio.ensure_future(client_talk(create_asyncio_eventloop(loop)))
    except ConnectionRefusedError:
        sys.stderr.write("Error connecting.\nQuitting.\n")
        return

    try:
        loop.run_forever()          # Now run forever except for a keyboard interrupt.
    except KeyboardInterrupt:
        pass
    loop.close()                    # Then close the event loop when done.


if __name__ == "__main__":
    main()
