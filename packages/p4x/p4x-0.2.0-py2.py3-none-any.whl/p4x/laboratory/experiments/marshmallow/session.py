from marshmallow import fields

from p4x.laboratory.experiments import session as _session
from p4x.laboratory.experiments.marshmallow import (
    base as _base,
    trial as _trial,
)

__author__ = "Philipp Tempel"
__email__ = "p.tempel@tudelft.nl"


class SessionSchema(_base.BaseSchema):
    name = fields.String(
            required=True,
    )
    path = fields.String(
            required=True,
    )
    trials = fields.List(
            fields.Nested(
                    _trial.TrialSchema(),
            ),
            required=False,
            missing=[],
    )

    __model__ = _session.Session


__all__ = [
        'SessionSchema',
]
