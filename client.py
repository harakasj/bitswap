from __future__ import unicode_literals

import asyncio
import sys
from pickle import dumps

from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.interface import CommandLineInterface
from prompt_toolkit.shortcuts import create_prompt_application, create_asyncio_eventloop, prompt_async

from chat_utils import Login, Sender, Request
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
            sys.stdout.flush()
            msg = msg.text
            try:
                if msg.startswith("/"):
                    msg = msg.split(sep="/")
                    if msg[1] == "bye":
                        client[0].close_conn()

                    elif msg[1] == "contacts":
                        client[0].send(Request("contacts", usr))

                    elif msg[1] == "send":
                        client[0].send(Sender(msg[2], msg[3]))
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
    loop = asyncio.get_event_loop()
    try:
        couroutine = loop.create_connection(Client, '192.168.1.2', 9999)
        loop.run_until_complete(couroutine)
        asyncio.async(client_talk(create_asyncio_eventloop(loop), couroutine))
    except ConnectionRefusedError:
        sys.stderr.write("Error connecting.\nQuitting.\n")
        return
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    loop.close()


if __name__ == "__main__":
    main()
