from getpass import getuser
from ..interfaces import ClientMode
from .clientservice import AnalyticToolClient
from .connection import ServerConnection


def run():
    username = getuser()
    key_file = open("/home/{}/.ayda/clientkey".format(username), "r")
    clientdata = key_file.readlines()
    server_address = clientdata[0][:-1]
    port = clientdata[1][:-1]
    mode = ClientMode[clientdata[2][:-1]]
    username = clientdata[3][:-1]
    pw = clientdata[4][:-1]
    client = AnalyticToolClient(
        ServerConnection(server_address, port, username, pw), mode
    )
    client.start()
