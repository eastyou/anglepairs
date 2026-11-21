"""anglepairs 的核心计算：角的分类、余角补角、三角形内角、钟面夹角与度分秒。"""

from __future__ import annotations

import math
import random
import re
from typing import Dict, List, Sequence

_EPS = 1e-9

CLASS_NAMES = ["零角", "锐角", "直角", "钝角", "平角", "优角", "周角"]

_CLASS_RULES = {
    "零角": "角 = 0°",
    "锐角": "0° < 角 < 90°",
    "直角": "角 = 90°",
    "钝角": "90° < 角 < 180°",
    "平角": "角 = 180°",
    "优角": "180° < 角 < 360°",
    "周角": "角 = 360°",
}

_PLAIN_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$")
_DMS_RE = re.compile(
    r"^(?P<sign>[+-]?)(?P<deg>\d+(?:\.\d+)?)\s*[°度]\s*"
    r"(?:(?P<min>\d+(?:\.\d+)?)\s*['′分]\s*)?"
    r"(?:(?P<sec>\d+(?:\.\d+)?)\s*[\"″秒]\s*)?$"
)


def _require_number(value: object, name: str) -> float:
    """把 value 校验并转换为有限浮点数，拒绝 bool、非数字、NaN 与无穷。"""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("%s必须是数字" % name)
    number = float(value)
    if math.isnan(number):
        raise ValueError("%s不能是 NaN" % name)
    if math.isinf(number):
        raise ValueError("%s必须是有限数字" % name)
    return number


def classify_angle(degrees: float) -> str:
    """按度数返回角的名称；超出 0~360 或为负数时抛出 ValueError。"""
    value = _require_number(degrees, "角度")
    if value < -_EPS or value > 360.0 + _EPS:
        raise ValueError("角度必须在 0 到 360 之间，当前为 %s" % _number_text(value))
    value = min(max(value, 0.0), 360.0)
    if abs(value) <= _EPS:
        return "零角"
    if value < 90.0 - _EPS:
        return "锐角"
    if abs(value - 90.0) <= _EPS:
        return "直角"
    if value < 180.0 - _EPS:
        return "钝角"
    if abs(value - 180.0) <= _EPS:
        return "平角"
    if value < 360.0 - _EPS:
        return "优角"
    return "周角"


def complement(degrees: float) -> float:
    """求余角：仅当 0 < 角 < 90 时有意义。"""
    value = _require_number(degrees, "角度")
    if value <= _EPS or value >= 90.0 - _EPS:
        raise ValueError("只有大于 0 且小于 90 的角才有余角，当前为 %s" % _number_text(value))
    return 90.0 - value


def supplement(degrees: float) -> float:
    """求补角：仅当 0 < 角 < 180 时有意义。"""
    value = _require_number(degrees, "角度")
    if value <= _EPS or value >= 180.0 - _EPS:
        raise ValueError("只有大于 0 且小于 180 的角才有补角，当前为 %s" % _number_text(value))
    return 180.0 - value


def third_angle(first: float, second: float) -> float:
    """已知三角形两个内角，求第三个内角。"""
    one = _require_number(first, "第一个角")
    two = _require_number(second, "第二个角")
    if one <= _EPS or two <= _EPS:
        raise ValueError("三角形的两个已知角都必须大于 0")
    if one + two >= 180.0 - _EPS:
        raise ValueError("两个已知角之和必须小于 180，当前为 %s" % _number_text(one + two))
    return 180.0 - one - two


def is_valid_triangle_angles(first: float, second: float, third: float) -> bool:
    """判断三个角能否构成三角形：均为正角且和约为 180（容差 1e-9）。"""
    one = _require_number(first, "第一个角")
    two = _require_number(second, "第二个角")
    three = _require_number(third, "第三个角")
    if one <= 0.0 or two <= 0.0 or three <= 0.0:
        return False
    return abs(one + two + three - 180.0) <= 1e-9


def clock_angle(hour: int, minute: int) -> float:
    """返回钟面上时针与分针的最小夹角，取值 0~180，支持 12 小时循环。"""
    if isinstance(hour, bool) or not isinstance(hour, int):
        raise ValueError("小时必须是整数")
    if isinstance(minute, bool) or not isinstance(minute, int):
        raise ValueError("分钟必须是整数")
    if hour < 0 or hour > 23:
        raise ValueError("小时必须在 0 到 23 之间，当前为 %d" % hour)
    if minute < 0 or minute > 59:
        raise ValueError("分钟必须在 0 到 59 之间，当前为 %d" % minute)
    hour_angle = (hour % 12) * 30.0 + minute * 0.5
    minute_angle = minute * 6.0
    difference = abs(hour_angle - minute_angle)
    return min(difference, 360.0 - difference)


def parse_dms(text: str) -> float:
    """解析「30°15'30"」形式的度分秒，也接受 30°15′30″ 与纯度数。"""
    if not isinstance(text, str):
        raise ValueError("角度文本必须是字符串")
    value = text.strip()
    if not value:
        raise ValueError("角度文本不能为空")
    if _PLAIN_RE.match(value):
        return float(value)
    match = _DMS_RE.match(value)
    if match is None:
        raise ValueError("无法识别的角度格式：%s" % text)
    degrees = float(match.group("deg"))
    minutes = float(match.group("min")) if match.group("min") else 0.0
    seconds = float(match.group("sec")) if match.group("sec") else 0.0
    if minutes >= 60.0:
        raise ValueError("分必须小于 60，当前为 %s" % _number_text(minutes))
    if seconds >= 60.0:
        raise ValueError("秒必须小于 60，当前为 %s" % _number_text(seconds))
    total = degrees + minutes / 60.0 + seconds / 3600.0
    if match.group("sign") == "-":
        total = -total
    return total


def format_dms(degrees: float) -> str:
    """把度数格式化为度分秒，自动处理进位与浮点误差。"""
    value = _require_number(degrees, "角度")
    sign = "-" if value < 0 else ""
    total_seconds = int(round(abs(value) * 3600.0))
    deg, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "%s%d°%02d'%02d\"" % (sign, deg, minutes, seconds)


def _number_text(value: float) -> str:
    """把数字格式化成简洁文本，去掉多余的小数零。"""
    text = "%.4f" % value
    text = text.rstrip("0").rstrip(".")
    if text in ("", "-0"):
        return "0"
    return text


def _degree_text(value: float) -> str:
    return "%s°" % _number_text(value)


def _numeric_choices(
    correct: float, extras: Sequence[float], rng: random.Random
) -> List[str]:
    """生成 4 个互不相同的数值选项，并打乱顺序。"""
    correct_text = _degree_text(correct)
    texts = [correct_text]
    seen = {correct_text}
    pending = list(extras)
    offset = 5.0
    attempts = 0
    while len(texts) < 4 and attempts < 500:
        attempts += 1
        if pending:
            candidate = pending.pop(0)
        else:
            candidate = correct + offset
            offset += 5.0
        if not isinstance(candidate, (int, float)) or candidate <= 0:
            continue
        text = _degree_text(float(candidate))
        if text in seen:
            continue
        seen.add(text)
        texts.append(text)
    if len(texts) != 4:
        raise ValueError("无法生成足够的选项")
    rng.shuffle(texts)
    return texts


def _classify_item(rng: random.Random) -> Dict[str, object]:
    degrees = rng.choice(
        [0, 15, 30, 45, 60, 89, 90, 91, 120, 135, 150, 179, 180, 181, 220, 270, 300, 359, 360]
    )
    name = classify_angle(degrees)
    options = [name]
    for other in rng.sample([item for item in CLASS_NAMES if item != name], 3):
        options.append(other)
    rng.shuffle(options)
    return {
        "type": "classify",
        "question": "一个角是 %s，它属于哪一类角？" % _degree_text(float(degrees)),
        "answer": name,
        "options": options,
        "explanation": "%s 满足「%s」，因此是%s。"
        % (_degree_text(float(degrees)), _CLASS_RULES[name], name),
    }


def _complement_item(rng: random.Random) -> Dict[str, object]:
    degrees = rng.randint(1, 89)
    correct = complement(degrees)
    options = _numeric_choices(
        correct, [degrees, 180.0 - degrees, 90.0 + degrees, 45.0, 60.0], rng
    )
    return {
        "type": "complement",
        "question": "一个角是 %s，它的余角是多少度？" % _degree_text(float(degrees)),
        "answer": _degree_text(correct),
        "options": options,
        "explanation": "互为余角的两个角之和为 90°，90° - %s = %s。"
        % (_degree_text(float(degrees)), _degree_text(correct)),
    }


def _supplement_item(rng: random.Random) -> Dict[str, object]:
    degrees = rng.randint(1, 179)
    correct = supplement(degrees)
    options = _numeric_choices(
        correct,
        [degrees, 90.0 - degrees, 90.0 + degrees, 45.0, 180.0 + degrees],
        rng,
    )
    return {
        "type": "supplement",
        "question": "一个角是 %s，它的补角是多少度？" % _degree_text(float(degrees)),
        "answer": _degree_text(correct),
        "options": options,
        "explanation": "互为补角的两个角之和为 180°，180° - %s = %s。"
        % (_degree_text(float(degrees)), _degree_text(correct)),
    }


def _triangle_item(rng: random.Random) -> Dict[str, object]:
    first = rng.randint(10, 140)
    second = rng.randint(10, 170 - first)
    correct = third_angle(first, second)
    options = _numeric_choices(
        correct,
        [first + second, 180.0 - first, 180.0 - second, 90.0],
        rng,
    )
    return {
        "type": "triangle",
        "question": "三角形的一个内角是 %s，另一个内角是 %s，第三个内角是多少度？"
        % (_degree_text(float(first)), _degree_text(float(second))),
        "answer": _degree_text(correct),
        "options": options,
        "explanation": "三角形内角和为 180°，180° - %d° - %d° = %s。"
        % (first, second, _degree_text(correct)),
    }


def _clock_item(rng: random.Random) -> Dict[str, object]:
    hour = rng.randint(0, 23)
    minute = rng.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
    correct = clock_angle(hour, minute)
    extras = [
        360.0 - correct,
        correct + 15.0,
        correct - 15.0,
        180.0 - correct,
        correct / 2.0 if correct else 30.0,
    ]
    options = _numeric_choices(correct, extras, rng)
    hour_angle = (hour % 12) * 30.0 + minute * 0.5
    minute_angle = minute * 6.0
    return {
        "type": "clock",
        "question": "钟面上 %02d:%02d 时，时针与分针的最小夹角是多少度？" % (hour, minute),
        "answer": _degree_text(correct),
        "options": options,
        "explanation": "分针为 %s°，时针为 %s°，取最小夹角后为 %s。"
        % (_degree_text(minute_angle), _degree_text(hour_angle), _degree_text(correct)),
    }


_ITEM_BUILDERS = [_classify_item, _complement_item, _supplement_item, _triangle_item, _clock_item]


def make_quiz(count: int, seed: int) -> List[Dict[str, object]]:
    """生成可复现的 4 选 1 练习，覆盖分类、余角、补角、三角形与钟面夹角。"""
    if isinstance(count, bool) or not isinstance(count, int):
        raise ValueError("题目数量必须是整数")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("随机种子必须是整数")
    if count < 0:
        raise ValueError("题目数量不能为负数")
    if count > 500:
        raise ValueError("题目数量不能超过 500")
    rng = random.Random(seed)
    kinds = [index % len(_ITEM_BUILDERS) for index in range(count)]
    rng.shuffle(kinds)
    items: List[Dict[str, object]] = []
    for kind in kinds:
        items.append(_ITEM_BUILDERS[kind](rng))
    return items
