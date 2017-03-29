from collections import namedtuple
from time import gmtime, strftime

from prompt_toolkit.styles import style_from_dict
from pygments.style import Style
from pygments.styles.default import DefaultStyle
from pygments.token import Token


class DocumentStyle(Style):
    styles = {
        Token.Menu.Completions.Completion.Current: 'bg:#00aaaa #000000',
        Token.Menu.Completions.Completion: 'bg:#008888 #ffffff',
        Token.Menu.Completions.ProgressButton: 'bg:#003333',
        Token.Menu.Completions.ProgressBar: 'bg:#00aaaa',
    }
    styles.update(DefaultStyle.styles)


style = style_from_dict({
    Token.Toolbar: '#ffffff bg:#333333',
})


def toolbar_tokens(cli):
    return [(Token.Toolbar, " "), (Token.Toolbar, "Connected"), (Token.Toolbar, "status = Running")]


def tstamp():
    return strftime("%H:%M:%S", gmtime())


Connect = namedtuple("Connection", "addr port")
Login = namedtuple("Login", "username pwd")
# Login = namedtuple("Login", "action username pwd")
Message = namedtuple("Message", "rcv msg")
Sender = namedtuple("Sender", "rcv msg")
Request = namedtuple("Request", "req args")

