"""anglepairs：面向课堂的角的分类与计算小工具。"""

from .model import (
    classify_angle,
    clock_angle,
    complement,
    format_dms,
    is_valid_triangle_angles,
    make_quiz,
    parse_dms,
    supplement,
    third_angle,
)
from .render import angle_svg, worksheet_html

__all__ = [
    "angle_svg",
    "classify_angle",
    "clock_angle",
    "complement",
    "format_dms",
    "is_valid_triangle_angles",
    "make_quiz",
    "parse_dms",
    "supplement",
    "third_angle",
    "worksheet_html",
]

__version__ = "0.1.0"
