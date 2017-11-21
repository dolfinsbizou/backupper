import os

from .utils import *

_all_ = ["DummyStorage"]

class DummyStorage(AbstractStorageContext):
    """
        Dummy storage system.

        Just a demo implementation of backupper.connect.AbstractStorageContext. It will only store a non-persistent tree.
    """

    CONNEXION_TYPE = "dummy"

    def __init__(self):
        self._tree = {
            "file": "prout prout prout (je suis un enfant)",
            "dir": {
                "a": "",
                "b": "foo",
                "C": {
                    "D": {
                        "f": "Lol",
                        "G": {
                        }
                    },
                    "E": {
                    }
                }
            }
        }
        """Dummy file structure"""

        self._cwd = "/"
        """Dummy current working directory"""

        self._connected = False
        """True if connected"""

    def connect(self):
        # Does nothing else but toggleing a boolean
        if not self._connected:
            self._connected = True
        else:
            raise AlreadyConnectedError("connect: Already connected.")

    def disconnect(self):
        # Does nothing else but toggleing a boolean and deleting the tree
        if self._connected:
            self._connected = False
            self._tree = {}
            self._cwd = "/"
        else:
            raise NotConnectedError("disconnect: Not connected.")

    def upload(self, src, dest="."):
        pass

    def download(self, src, dest="."):
        pass

    def listdir(self, path="."):
        if self._connected:
            # Try to walk to the target directory
            try:
                result = self._walk(path)

                # If the target was a file we raise an exception
                if isinstance(result, dict):
                    return list(result.keys())
                else:
                    raise UnpermittedOperationError("listdir: {} isn't a directory.".format(path))
            except NotFoundError:
                raise NotFoundError("listdir: {} doesn't exist".format(path))
        else:
            raise NotConnectedError("listdir: Not connected.")


    def remove(self, path):
        if self._connected:
            basefile, to_remove = os.path.split(os.path.normpath(os.path.join(self._cwd, path)))

            # Try to walk to the base directory
            try:
                base = self._walk(basefile)

                # If the target resource doesn't exist we raise an exception
                if not to_remove in base:
                    raise NotFoundError("remove: {} doesn't exist.".format(path))

                del base[to_remove]
            except NotFoundError:
                raise NotFoundError("remove: {} doesn't exist".format(basefile))
        else:
            raise NotConnectedError("remove: Not connected.")

    def mkdir(self, path):
        if self._connected:
            basefile, new_dir = os.path.split(os.path.normpath(os.path.join(self._cwd, path)))

            # Try to walk to the base directory
            try:
                base = self._walk(basefile)

                # If the basefile is a regular file we raise an exception
                if not isinstance(base, dict):
                    raise UnpermittedOperationError("mkdir: {} is a file.".format(basefile))

                # If the target directory already exists we raise an exception
                if new_dir in base:
                    raise UnpermittedOperationError("mkdir: {} already exists.".format(path))

                # A dict is mutable so self._walk returns a reference we can directly modify
                base[new_dir] = {}
            except NotFoundError:
                raise NotFoundError("mkdir: {} doesn't exist.".format(basefile))
        else:
            raise NotConnectedError("mkdir: Not connected.")

    def rename(self, path, new_path):
        pass

    def chdir(self, path="/"):
        if self._connected:
            # Try to walk to the target directory
            try:
                # If the target is a file, we raise an exception
                if not isinstance(self._walk(path), dict):
                    raise UnpermittedOperationError("chdir: {} isn't a directory.".format(path))
            except NotFoundError:
                raise NotFoundError("chdir: {} doesn't exist.".format(path))

            # Set the new path
            new_path = os.path.normpath(os.path.join(self._cwd, path))
            self._cwd = new_path
        else:
            raise NotConnectedError("chdir: Not connected.")

    def getcwd(self):
        if self._connected:
            return self._cwd
        else:
            raise NotConnectedError("getcwd: Not connected.")

    def _walk(self, path):
        """
            Walks into the tree and returns the reached level.

            :param path: Absolute or relative path.
            :type path: str
            :return: The last level reached (a dictionary if it's a directory, a string if it's a file).
            :rtype: dict or str

            :raises: backupper.connect.utils.NotFoundError
        """

        # Absolute path
        canonical_path = os.path.normpath(os.path.join(self._cwd, path))

        splitted_path = []

        # Split the path from the end to the beginning (splitted_path is reversed)
        while canonical_path != "/":
            canonical_path, tail = os.path.split(canonical_path)
            splitted_path.append(tail)

        subtree = self._tree

        # Try to go to the target level
        for element in reversed(splitted_path):
            # If the element isn't in the subtree, we raise an exception
            if element in subtree:
                subtree = subtree[element]
            else:
                raise NotFoundError("_walk: {} doesn't exist.".format(path))

        return subtree
