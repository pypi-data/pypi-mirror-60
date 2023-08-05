from typing import AnyStr, Iterable, Optional

__author__ = "Philipp Tempel"
__email__ = "p.tempel@tudelft.nl"

UNITS = {
        "nsec": 1e-9,
        "usec": 1e-6,
        "msec": 1e-3,
        "sec":  1.0,
}


def format_time(dt,
                time_unit: Optional[AnyStr] = None,
                precision: Optional[int] = None):
    if isinstance(dt, Iterable):
        return [format_time(dt_, time_unit, precision) for dt_ in dt]

    unit = time_unit

    if unit is not None:
        scale = UNITS[unit]
    else:
        scales = [(scale, unit) for unit, scale in UNITS.items()]
        scales.sort(reverse=True)
        for scale, unit in scales:
            if dt >= scale:
                break

    return "%.*g %s" % (precision if precision is not None else 3,
                        dt / scale, unit)


__all__ = [
        'format_time',
]
