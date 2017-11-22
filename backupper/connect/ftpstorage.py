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
        if self._connection is None:
            raise NotConnectedError("upload: you're not connected to {}.".format(self.host))

        try:
            pass
        except Exception as e:
            raise StorageError("upload: FTP module returned an error ({}).".format(e))

    def download(self, src, dest="."):
        if self._connection is None:
            raise NotConnectedError("download: you're not connected to {}.".format(self.host))

        try:
            pass
        except Exception as e:
            raise StorageError("download: FTP module returned an error ({}).".format(e))

    def listdir(self, path="."):
        if self._connection is None:
            raise NotConnectedError("listdir: you're not connected to {}.".format(self.host))

        last_path = self.getcwd()
        abs_path = os.path.normpath(os.path.join(last_path, path))

        try:
            self.chdir(abs_path)
            result = [os.path.basename(f) for f in self._connection.nlst("-a") if not os.path.basename(f) in [".", "..", ""]]
            self.chdir(last_path)
            return result
        except Exception as e:
            self.chdir(last_path)
            raise StorageError("listdir: FTP module returned an error ({}).".format(e))


    def remove(self, path):
        if self._connection is None:
            raise NotConnectedError("remove: you're not connected to {}.".format(self.host))

        basename, filename = os.path.split(os.path.normpath(os.path.join(self.getcwd(), path)))
        files = {}

        try:
            list_log = []
            self._connection.dir(basename, list_log.append)
            files = {' '.join(line.split()[8:]): line[0] for line in list_log}
        except Exception as e:
            raise StorageError("remove: FTP module returned an error ({}).".format(e))

        if not filename in files:
            raise NotFoundError("remove: {} doesn't exist.".format(path))

        try:
            if files[filename] == "d":
                self._connection.rmd(path)
            else:
                self._connection.delete(path)
        except Exception as e:
            raise StorageError("remove: FTP module returned an error ({}).".format(e))

    def mkdir(self, path):
        if self._connection is None:
            raise NotConnectedError("mkdir: you're not connected to {}.".format(self.host))

        try:
            self._connection.mkd(path)
        except Exception as e:
            raise StorageError("mkdir: FTP module returned an error ({}).".format(e))

    def rename(self, path, new_path):
        if self._connection is None:
            raise NotConnectedError("rename: you're not connected to {}.".format(self.host))

        try:
            self._connection.rename(path, new_path)
        except Exception as e:
            raise StorageError("rename: FTP module returned an error ({}).".format(e))

    def chdir(self, path="/"):
        if self._connection is None:
            raise NotConnectedError("chdir: you're not connected to {}.".format(self.host))

        try:
            self._connection.cwd(path)
        except Exception as e:
            raise NotFoundError("chdir: FTP module returned an error ({}).".format(e))

    def getcwd(self):
        if self._connection is None:
            raise NotConnectedError("getcwd: you're not connected to {}.".format(self.host))

        try:
            return self._connection.pwd()
        except Exception as e:
            raise StorageError("getcwd: FTP module returned an error ({}).".format(e))
