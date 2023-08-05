from marshmallow import fields

from p4x.laboratory.experiments import project as _project
from p4x.laboratory.experiments.marshmallow import (
    base as _base,
    session as _session,
)

__author__ = "Philipp Tempel"
__email__ = "p.tempel@tudelft.nl"


class ProjectSchema(_base.BaseSchema):
    name = fields.String(
            required=True,
    )
    path = fields.String(
            required=True,
    )
    sessions = fields.List(
            fields.Nested(
                    _session.SessionSchema(),
            ),
            required=False,
            missing=[],
    )

    __model__ = _project.Project


__all__ = [
        'ProjectSchema',
]
