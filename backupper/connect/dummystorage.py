import os

from .utils import *

_all_ = ["DummyStorage"]

class DummyStorage(AbstractStorageContext):
    """
        Dummy storage system.

        Just a demo implementation of .connect.AbstractStorageContext. It will only store a non-persistent tree.
    """

    CONNEXION_TYPE = "dummy"

    def __init__(self):
        self._tree = {}
        """Dummy file structure"""
        self._cwd = "/"
        """Dummy current working directory"""
        self._connected = False

    def connect(self):
        if not self._connected:
            self._connected = True
        else:
            raise AlreadyConnectedError("You tried to open a connection but you're already connected.")

    def disconnect(self):
        if self._connected:
            self._connected = False
            self._tree = {}
            self._cwd = "/"
        else:
            raise NotConnectedError("You tried to close a connection but you're not connected.")

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

    def chdir(self, path="."):
        # TODO check if existent in tree
        if self._connected:
            new_path = os.path.normpath(os.path.join(self._cwd, path))
            self._cwd = new_path
        else:
            raise NotConnectedError("Unable to chdir: not connected.")

    def getcwd(self):
        if self._connected:
            return self._cwd
        else:
            raise NotConnectedError("Unable to getcwd: not connected.")
