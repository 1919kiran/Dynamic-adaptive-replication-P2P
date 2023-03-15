import threading

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


def start_ftp_server():
    authorizer = DummyAuthorizer()
    authorizer.add_user(username="node", password="password", homedir="files/", perm='elradfmwMT')
    handler = FTPHandler
    handler.authorizer = authorizer
    server = FTPServer(("0.0.0.0", 20), handler)
    server.serve_forever()
    return "FTP server started"


# Start the FTP server in a separate thread
ftp_thread = threading.Thread(target=start_ftp_server)
ftp_thread.start()


