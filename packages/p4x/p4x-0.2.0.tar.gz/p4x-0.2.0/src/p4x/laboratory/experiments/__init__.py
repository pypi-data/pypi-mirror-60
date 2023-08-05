from p4x.laboratory.experiments import manager as _manager
from p4x.laboratory.experiments.project import Project
from p4x.laboratory.experiments.session import Session
from p4x.laboratory.experiments.trial import Trial

__author__ = "Philipp Tempel"
__email__ = "p.tempel@tudelft.nl"

Manager = _manager.Manager()

__all__ = [
        'Manager',
        'Session',
        'Project',
        'Trial',
]
