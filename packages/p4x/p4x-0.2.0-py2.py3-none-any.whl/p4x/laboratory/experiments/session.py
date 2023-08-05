import pathlib as pl
from typing import List, Optional, Union

from magic_repr import make_repr
from p4x.laboratory.experiments import (
    base as _base,
    project as _project,
    trial as _trial,
)

__author__ = "Philipp Tempel"
__email__ = "p.tempel@tudelft.nl"


class Session(_base.BaseObject):
    """

    """

    """
    List of directories additional to a session
    """
    DIRECTORIES = (_base.MEDIA_FOLDER, )

    def __init__(self,
                 name: str,
                 path: Union[str, pl.Path],
                 trials: Optional[List['_trial.Trial']] = None):
        super().__init__(name, path)
        self.trials = trials or []

    @property
    def num_trials(self):
        return self.num_children

    @property
    def project(self):
        return self.parent

    @project.setter
    def project(self, project: '_project.Project'):
        self.parent = project

    @project.deleter
    def project(self):
        del self.parent

    @property
    def trials(self):
        return self.children

    @trials.setter
    def trials(self, trials: List['_trial.Trial']):
        self.children = trials

    @trials.deleter
    def trials(self):
        del self.children

    __repr__ = make_repr(
            'name',
            'path',
            'trials',
    )


__all__ = [
        'Session',
]
