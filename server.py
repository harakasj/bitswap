from __future__ import unicode_literals

import asyncio
import sys
from pickle import loads

from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.interface import CommandLineInterface
from prompt_toolkit.shortcuts import create_prompt_application, create_asyncio_eventloop

from chat_utils import Login, Sender, Request
from chat_utils import toolbar_tokens
from chat_utils import tstamp
from database import Database

cmd_complete = WordCompleter(['/send', '/bye'], ignore_case=True)
sql_completer = WordCompleter(['create', 'select', 'insert', 'drop',
                               'delete', 'from', 'where', 'table'], ignore_case=True)

async def server_console(loop):
    history = InMemoryHistory()
    cli = CommandLineInterface(
        application=create_prompt_application('> ',
            completer=cmd_complete,
            history=history,
            get_bottom_toolbar_tokens=toolbar_tokens ), 
            eventloop=loop
    )

    sys.stdout = cli.stdout_proxy()
    while True:
        try:
            result = await cli.run_async()
            for client in clients:
                client.send(result.text)
        except (EOFError, KeyboardInterrupt):
            return

clients = []
cList ={}


# ===============================================================================
class Server(asyncio.Protocol):
    db = Database()
    db.connect()

    def connection_made(self, transport):
        self.transport = transport
        peername = transport.get_extra_info("peername")
        self.username = ""
        self.addr = "{:s}:{:d}".format(*peername)
        print("{0:s}: {1:s} connected".format(tstamp(), self.addr))
        self.send("connected")
        clients.append(self)

    def data_received(self, data):
        data = loads(data)
        print(tstamp()+" received: {}\n".format(data) )
        if len(data) == 0:
            return

        if type(data) == Login:
            self.handle_login(data)
                    
        if type(data) == Sender:
            self.handle_message(data)
        
        if type(data) == Request:
            self.handle_request(data)
        
    def connection_lost(self, ex):
        print("{0:s} connection lost: {1:s}".format(tstamp(),self.username) )
        clients.remove(self)
        del cList[self.username]

        # Fix this
        for client in clients:
            client.send("{:s} disconnected".format(self.username))



    def send(self,text,*args):
        if args:
            self.transport.write("{0:s} [{1:s}]: {2:s}\n".format(tstamp(),*args, text).encode())
        else:
            self.transport.write("{0:s} [SERVER]: {1:s}\n".format(tstamp(),text).encode())

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
            print( *tuple( contacts[i] for i in range( len(contacts) ) ),sep="\n" )
            
            for c in contacts:
                self.send("{}".format(c))
        
# ===============================================================================

if __name__ == '__main__':
    print("{0:s} [SERVER]: starting.".format(tstamp() ))
    loop = asyncio.get_event_loop()
    coroutine = loop.create_server(Server, '192.168.1.2', 9999)
    
    server = loop.run_until_complete(coroutine)
    asyncio.async(server_console(create_asyncio_eventloop(loop)))
    for socket in server.sockets:
        print("{0:s} [SERVER]: running on {1:}".format(tstamp(),socket.getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass