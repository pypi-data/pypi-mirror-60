from marshmallow import fields

from p4x.laboratory.experiments import trial as _trial
from p4x.laboratory.experiments.marshmallow import base as _base

__author__ = "Philipp Tempel"
__email__ = "p.tempel@tudelft.nl"


class TrialSchema(_base.BaseSchema):
    name = fields.String(
            required=True,
    )
    path = fields.String(
            required=True,
    )

    __model__ = _trial.Trial


__all__ = [
        'TrialSchema',
]
