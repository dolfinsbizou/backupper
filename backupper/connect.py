"""
    Provides an abstraction layer to open a connection to various storage systems.
"""

from abc import ABC, abstractmethod

__all__ = []

class AbstractStorageContext(ABC):
    """
        Abstract connection model.

        This class provides a common context for a connection to a distant storage. Implementation is left to child classes.
    """

    type = "unknown"
    """Type of storage (may be FTP, SFTP, S3, etc.)."""

    def __init__(self):
        pass

    @abstractmethod
    def connect():
    """
        Opens a connection with the storage.
    """
        pass

    @abstractmethod
    def disconnect():
    """
        Closes the connection with the storage.
    """
        pass

    @abstractmethod
    def upload(src, dest="."):
    """
        Uploads a file to the storage.

        :param src: Local path of the file or directory to upload.
        :type src: str
        :param dest: Distant destination path.
        :type dest: str
    """
        pass

    @abstractmethod
    def download(src, dest="."):
    """
        Retrieves a file from the storage.

        :param src: Distant path of the file or directory to retrieve.
        :type src: str
        :param dest: Local destination path.
        :type dest: str
    """
        pass

    @abstractmethod
    def listdir():
    """
        Lists the contents of the storage.
    """
        pass

    @abstractmethod
    def chdir(path="."):
    """
        Changes the storage working directory.

        :param path: New distant working directory.
        :type path: str
    """
        pass

    @abstractmethod
    def remove(path):
    """
        Removes a file or directory from the storage.

        :param path: Resource to remove.
        :type path: str
    """
        pass

    @abstractmethod
    def getcwd():
    """
        Returns the storage working directory.

        :return: Current distant working directory.
        :rtype: str
    """
        pass
