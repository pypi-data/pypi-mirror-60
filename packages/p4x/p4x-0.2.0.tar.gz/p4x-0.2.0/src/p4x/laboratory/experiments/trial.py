from magic_repr import make_repr
from p4x.laboratory.experiments import base as _base, session as _session

__author__ = "Philipp Tempel"
__email__ = "p.tempel@tudelft.nl"


class Trial(_base.BaseObject):
    """

    """

    """
    List of directories additional to a trials
    """
    DIRECTORIES = (_base.MEDIA_FOLDER, _base.DATA_FOLDER)

    @property
    def children(self):
        raise AttributeError("'Trial' object has no attribute 'children'")

    @property
    def session(self):
        return self._parent

    @session.setter
    def session(self, session: '_session.Session'):
        self._parent = session

    @session.deleter
    def session(self):
        del self._parent

    __repr__ = make_repr(
            'name',
            'path',
    )


__all__ = [
        'Trial',
]
