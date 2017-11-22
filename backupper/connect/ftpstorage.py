import os
from ftplib import FTP

from .utils import *

_all_ = ["FTPStorage"]

class FTPStorage(AbstractStorageContext):
    """
        FTP storage system.

        A handy wrapper for ftplib.FTP methods.
    """

    CONNEXION_TYPE = "ftp"

    def __init__(self, host, user="anonymous", passwd=""):
        if not host:
            raise ValueError("__init__: please provide a host.")
        self.host = host
        self.user = user
        self.passwd = passwd
        self._connection = None

    def connect(self):
        if not self._connection is None:
            raise AlreadyConnectedError("connect: you're already connected to {}.".format(self._connection.host)) # We use self._connection.host because the user could modify the host after the connection was opened

        try:
            self._connection = FTP(host=self.host)
            self._connection.login(user=self.user, passwd=self.passwd)
        except Exception as e:
            if not self._connection is None:
                self._connection.close()
            raise UnableToConnectError("connect: FTP module returned an error ({}).".format(e))

    def disconnect(self):
        if self._connection is None:
            raise NotConnectedError("disconnect: you're not connected to {}.".format(self.host))

        try:
            self._connection.quit()
        except:
            self._connection.close()
        finally:
            self._connection = None

    def upload(self, src, dest="."):
        pass

    def download(self, src, dest="."):
        pass

    def listdir(self, path="."):
        pass

    def remove(self, path):
        pass

    def mkdir(self, path):
        pass

    def rename(self, path, new_path):
        pass

    def chdir(self, path="/"):
        pass

    def getcwd(self):
        pass
