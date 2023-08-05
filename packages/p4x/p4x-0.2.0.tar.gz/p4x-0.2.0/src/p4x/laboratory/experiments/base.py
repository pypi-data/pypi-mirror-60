import json
import os
import sys
import pathlib as pl
import shutil
from typing import Any, Dict, List, Union

__author__ = "Philipp Tempel"
__email__ = "p.tempel@tudelft.nl"

CONFIG_NAME = 'config'
DATA_FOLDER = 'data'
INPUT_NAME = 'input'
MEDIA_FOLDER = 'media'
SCOPE_NAME = 'scope'


class BaseObject(os.PathLike):
    """

    """
    _name: str
    _children: List['BaseObject']
    _parent: 'BaseObject'
    _path: pl.Path

    """
    List of directories additional to an object
    """
    DIRECTORIES = ()

    def __init__(self, name: str, path: Union[str, pl.Path]):
        self._name = name
        self._path = pl.Path(path)
        # init protected variables
        self._children = []
        self._config = None
        self._parent = None
        self._cwd = os.getcwd()

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, children: List['BaseObject']):
        for child in children:
            # make sure parent points to the right object
            child.parent = self
            # # make sure non-absolute children path's inherit the path from its
            # # parent
            # if not child.path.is_absolute():
            #     child._path = self.path / child.path

        self._children = children

    @children.deleter
    def children(self):
        del self._children

    @property
    def config(self):
        if self._config is None:
            self.load_config()

        return self._config

    @config.setter
    def config(self, config: Dict[str, Any]):
        # store locally
        self._config = config

    @config.deleter
    def config(self):
        del self._config

    @property
    def config_path(self):
        """
        Return absolute path to the object's `config.json` file
        """
        return self.path / f'{CONFIG_NAME}.json'

    @property
    def media_path(self):
        """
        Return absolute path to the object's `media` directory
        """
        return self.path / MEDIA_FOLDER

    @property
    def media(self):
        """
        Return all files inside the `media` directory
        """
        return self.media_path.resolve().rglob('*')

    @property
    def name(self):
        return self._name

    @property
    def num_children(self):
        return len(self._children)

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent: 'BaseObject'):
        self._parent = parent

    @parent.deleter
    def parent(self):
        del self._parent

    @property
    def path(self):
        """
        Return absolute path to the object's directory
        """
        if not self._path.is_absolute():
            try:
                return self.parent.path / self._path
            except AttributeError:
                return self._path
        return self._path

    def blueprint(self):
        """
        Create the blueprint directory and file structure for the object
        """
        if self._path.resolve().exists():
            raise ValueError(f'{self.__class__.__name__} already exists.')

        try:
            # create the main directory
            self.path.mkdir(parents=True, exist_ok=True)

            #
            for directory in self.DIRECTORIES:
                (self.path / directory).mkdir(parents=True, exist_ok=True)

            # save configuration file
            self.save_config()

            # finally, create all child objects
            for child in self._children:
                child.blueprint()
        except ValueError:
            if self.path.exists():
                shutil.rmtree(str(self.path), ignore_errors=True)

    def chdir(self):
        os.chdir(self.path.resolve())

    def addpath(self):
        sys.path.append(self.path)

    def rmpath(self):
        sys.path.remove(self.path)

    def exists(self):
        return self.path.exists()

    def glob(self, pattern):
        return self.path.glob(pattern)

    def load_config(self):
        """
        Load configuration from file and store inside the object
        """
        try:
            self._config = json.load(self.config_path.resolve().open('r'))
        except FileNotFoundError:
            self._config = {}

    def rglob(self, pattern):
        return self.path.rglob(pattern)

    def save_config(self):
        """
        Save config to `config.json` file in the object's directory
        """

        json.dump(self.config, self.config_path.resolve().open('w'))

    def __iter__(self):
        return iter(self._children)

    def __hash__(self):
        return hash(self._path)

    def __fspath__(self):
        return str(self.path)

    def __enter__(self):
        self._cwd = os.getcwd()
        os.chdir(self.path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self._cwd)
        return self

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError()

        return self._path == other._path

    def __ne__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError()

        return self._path != other._path

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError()

        return self._path < other._path

    def __le__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError()

        return self._path <= other._path

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError()

        return self._path > other._path

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError()

        return self._path >= other._path

    def __truediv__(self, other):
        return self.path / other

    def __rtruediv__(self, other):
        return other / self.path


__all__ = [
        'BaseObject',
]
