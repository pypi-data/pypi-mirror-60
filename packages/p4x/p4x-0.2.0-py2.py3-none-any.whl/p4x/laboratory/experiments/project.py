import pathlib as pl
from typing import List, Optional, Union

from magic_repr import make_repr
from p4x.laboratory.experiments import session as _session, base as _base

__author__ = "Philipp Tempel"
__email__ = "p.tempel@tudelft.nl"


class Project(_base.BaseObject):
    """

    """

    """
    List of directories additional to a project
    """
    DIRECTORIES = (_base.MEDIA_FOLDER, )

    def __init__(self,
                 name: str,
                 path: Union[str, pl.Path],
                 sessions: Optional[List['_session.Session']] = None):
        super().__init__(name, path)
        self.sessions = sessions or []

    @property
    def num_sessions(self):
        return self.num_children

    @property
    def sessions(self):
        return self.children

    @sessions.setter
    def sessions(self, sessions: List['_session.Session']):
        self.children = sessions

    @sessions.deleter
    def sessions(self):
        del self.children

    __repr__ = make_repr(
            'name',
            'path',
            'sessions',
    )


__all__ = [
        'Project',
]
