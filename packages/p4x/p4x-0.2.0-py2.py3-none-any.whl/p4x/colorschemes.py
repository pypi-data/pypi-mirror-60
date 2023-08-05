from typing import AnyStr, Dict, Mapping

from colour import Color

__author__ = "Philipp Tempel"
__email__ = "p.tempel@tudelft.nl"


def ustutt() -> Dict[AnyStr, Color]:
    """
    Colors of University of Stuttgart, Stuttgart, Germany

    Returns
    -------
    colors : dict
        Dictionary of color where the key is the color's name, and the value
        is a Color object.

    """
    return {
            'cyan':      Color(rgb=(0 / 255, 166 / 255, 214 / 255)),
            'black':     Color(rgb=(0 / 255, 0 / 255, 0 / 255)),
            'dark_blue': Color(rgb=(159 / 255, 153 / 255, 154 / 255)),
            'yellow':    Color(rgb=(62 / 255, 68 / 255, 76 / 255)),
            'gray':      Color(rgb=(255 / 255, 213 / 255, 0 / 255)),
            'orange':    Color(rgb=(231 / 255, 81 / 255, 18 / 255))
    }


def tudelft() -> Mapping[AnyStr, Color]:
    """
    Colors of Delft University of Technology, Delft, The Netherlands

    Returns
    -------
    colors : dict
        Dictionary of color where the key is the color's name, and the value
        is a Color object.

    """
    return {
            'cyan':         Color(rgb=(0 / 255, 166 / 255, 214 / 255)),
            'black':        Color(rgb=(0 / 255, 0 / 255, 0 / 255)),
            'white':        Color(rgb=(255 / 255, 255 / 255, 255 / 255)),
            'sky_blue':     Color(rgb=(110 / 255, 187 / 255, 213 / 255)),
            'purple':       Color(rgb=(29 / 255, 28 / 255, 115 / 255)),
            'orange':       Color(rgb=(230 / 255, 70 / 255, 22 / 255)),
            'yellow':       Color(rgb=(225 / 255, 196 / 255, 0 / 255)),
            'red':          Color(rgb=(226 / 255, 26 / 255, 26 / 255)),
            'green':        Color(rgb=(0 / 255, 136 / 255, 145 / 255)),
            'bright_green': Color(rgb=(165 / 255, 202 / 255, 26 / 255)),
            'warm_purple':  Color(rgb=(109 / 255, 23 / 255, 127 / 255)),
            'grey_green':   Color(rgb=(107 / 255, 134 / 255, 137 / 255))
    }


USTUTT = ustutt()
TUDELFT = tudelft()

__all__ = [
        'USTUTT',
        'TUDELFT',
]
