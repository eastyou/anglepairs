"""anglepairs 的渲染层：SVG 角示意图与可打印练习页。"""

from __future__ import annotations

import html
import math
from collections import abc
from typing import Dict, List, Sequence

from .model import _require_number, classify_angle


def _svg_number(value: float) -> str:
    """把坐标或角度格式化成两位小数以内的简洁文本。"""
    text = "%.2f" % value
    text = text.rstrip("0").rstrip(".")
    if text in ("", "-0"):
        return "0"
    return text


def angle_svg(degrees: float) -> str:
    """生成带弧线与度数标注的 SVG 角示意图。"""
    value = _require_number(degrees, "角度")
    if value < 0.0 or value > 360.0:
        raise ValueError("角度必须在 0 到 360 之间，当前为 %s" % _svg_number(value))
    name = classify_angle(value)
    theta = math.radians(value)
    vertex_x, vertex_y = 120.0, 150.0
    ray_length = 105.0
    arc_radius = 38.0
    end_x = vertex_x + ray_length * math.cos(theta)
    end_y = vertex_y - ray_length * math.sin(theta)
    arc_x = vertex_x + arc_radius * math.cos(theta)
    arc_y = vertex_y - arc_radius * math.sin(theta)
    label_x = vertex_x + 60.0 * math.cos(theta / 2.0)
    label_y = vertex_y - 60.0 * math.sin(theta / 2.0) + 5.0

    parts: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 280" '
        'width="240" height="280" role="img" aria-label="%s度的%s示意图">'
        % (_svg_number(value), name),
        "<title>%s° %s</title>" % (_svg_number(value), name),
        '<rect width="240" height="280" fill="#ffffff"/>',
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#3b4a5a" stroke-width="3" '
        'stroke-linecap="round"/>'
        % (
            _svg_number(vertex_x),
            _svg_number(vertex_y),
            _svg_number(vertex_x + ray_length),
            _svg_number(vertex_y),
        ),
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#3b4a5a" stroke-width="3" '
        'stroke-linecap="round"/>'
        % (
            _svg_number(vertex_x),
            _svg_number(vertex_y),
            _svg_number(end_x),
            _svg_number(end_y),
        ),
    ]

    if 0.0 < value < 360.0:
        large_arc = 1 if value > 180.0 else 0
        parts.append(
            '<path d="M %s %s A %s %s 0 %d 0 %s %s" fill="none" stroke="#c2410c" '
            'stroke-width="2.5"/>'
            % (
                _svg_number(vertex_x + arc_radius),
                _svg_number(vertex_y),
                _svg_number(arc_radius),
                _svg_number(arc_radius),
                large_arc,
                _svg_number(arc_x),
                _svg_number(arc_y),
            )
        )
    elif value == 360.0:
        parts.append(
            '<circle cx="%s" cy="%s" r="%s" fill="none" stroke="#c2410c" stroke-width="2.5"/>'
            % (
                _svg_number(vertex_x),
                _svg_number(vertex_y),
                _svg_number(arc_radius),
            )
        )

    parts.extend(
        [
            '<circle cx="%s" cy="%s" r="4" fill="#3b4a5a"/>'
            % (_svg_number(vertex_x), _svg_number(vertex_y)),
            '<text x="%s" y="%s" text-anchor="middle" font-size="15" font-weight="600" '
            'fill="#c2410c" font-family="PingFang SC, Microsoft YaHei, sans-serif">%s°</text>'
            % (_svg_number(label_x), _svg_number(label_y), _svg_number(value)),
            '<text x="%s" y="272" text-anchor="middle" font-size="13" fill="#616e7c" '
            'font-family="PingFang SC, Microsoft YaHei, sans-serif">%s</text>'
            % (_svg_number(vertex_x), name),
            "</svg>",
        ]
    )
    return "\n".join(parts)


def _validated_items(items: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    """校验题目数据，返回只含标准字段的新列表。"""
    if isinstance(items, (str, bytes)) or not isinstance(items, abc.Sequence):
        raise TypeError("题目列表必须是列表或元组")
    result: List[Dict[str, object]] = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise TypeError("第 %d 题必须是字典" % index)
        for key in ("question", "answer", "options", "explanation"):
            if key not in item:
                raise ValueError("第 %d 题缺少字段 %s" % (index, key))
        question = item["question"]
        options = item["options"]
        answer = item["answer"]
        explanation = item["explanation"]
        if not isinstance(question, str) or not question.strip():
            raise ValueError("第 %d 题的题干必须是非空字符串" % index)
        if not isinstance(options, (list, tuple)) or len(options) != 4:
            raise ValueError("第 %d 题必须有 4 个选项" % index)
        for option in options:
            if not isinstance(option, str):
                raise ValueError("第 %d 题的选项必须是字符串" % index)
        if not isinstance(answer, str):
            raise ValueError("第 %d 题的答案必须是字符串" % index)
        if answer not in options:
            raise ValueError("第 %d 题的答案不在选项中" % index)
        if not isinstance(explanation, str):
            raise ValueError("第 %d 题的解析必须是字符串" % index)
        result.append(
            {
                "question": question,
                "answer": answer,
                "options": list(options),
                "explanation": explanation,
            }
        )
    return result


def worksheet_html(
    items: Sequence[Dict[str, object]], title: str, show_answers: bool = False
) -> str:
    """生成自包含、可打印的练习页；show_answers 为真时输出答案与解析。"""
    if not isinstance(title, str) or not title.strip():
        raise ValueError("页面标题必须是非空字符串")
    if not isinstance(show_answers, bool):
        raise ValueError("show_answers 必须是布尔值")
    data = _validated_items(items)
    mode = "答案与解析" if show_answers else "学生练习"
    blocks: List[str] = []
    for index, item in enumerate(data, start=1):
        options = item["options"]
        answer = item["answer"]
        correct_index = options.index(answer)
        option_lines: List[str] = []
        for offset, option in enumerate(options):
            tag = chr(ord("A") + offset)
            css = " correct" if show_answers and offset == correct_index else ""
            option_lines.append(
                '<li class="%s"><span class="tag">%s</span>%s</li>'
                % (css.strip(), tag, html.escape(option))
            )
        block = [
            '<section class="item">',
            "<h2>%d. %s</h2>" % (index, html.escape(item["question"])),
            '<ul class="options">%s</ul>' % "".join(option_lines),
        ]
        if show_answers:
            block.append(
                '<p class="answer">答案：%s</p>'
                % html.escape("%s. %s" % (chr(ord("A") + correct_index), answer))
            )
            block.append('<p class="explanation">解析：%s</p>' % html.escape(item["explanation"]))
        else:
            block.append('<p class="blank">答：____________________</p>')
        block.append("</section>")
        blocks.append("\n".join(block))

    body = "\n".join(blocks)
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<style>
:root{--ink:#1f2933;--muted:#616e7c;--line:#d9e2ec;--accent:#c2410c;--paper:#fff}
*{box-sizing:border-box}
body{margin:0;background:#f5f7fa;color:var(--ink);line-height:1.65;
font-family:"PingFang SC","Microsoft YaHei","Noto Sans SC",system-ui,sans-serif}
.page{max-width:820px;margin:24px auto;background:var(--paper);padding:40px 48px;
box-shadow:0 2px 12px rgba(15,23,42,.08)}
header{border-bottom:2px solid var(--ink);padding-bottom:16px;margin-bottom:20px}
h1{font-size:26px;margin:0 0 8px}
.meta{color:var(--muted);font-size:14px;margin:0}
.item{padding:14px 0;border-bottom:1px dashed var(--line);page-break-inside:avoid}
.item h2{font-size:16px;margin:0 0 8px;font-weight:600}
.options{list-style:none;padding:0;margin:0;display:grid;
grid-template-columns:1fr 1fr;gap:6px 16px}
.options li{padding:4px 8px;border-radius:4px}
.tag{display:inline-block;width:20px;font-weight:600;color:var(--muted)}
li.correct{background:#fff1e6;color:#9a3412;font-weight:600}
.blank{margin:8px 0 0;color:var(--muted)}
.answer{margin:8px 0 0;color:#9a3412}
.explanation{margin:4px 0 0;color:var(--muted);font-size:14px}
footer{margin-top:24px;padding-top:12px;border-top:1px solid var(--line);
color:var(--muted);font-size:12px;text-align:center}
@media print{body{background:#fff}.page{box-shadow:none;margin:0;max-width:none;padding:0}
@page{margin:16mm}}
</style>
</head>
<body>
<div class="page">
<header>
<h1>%(safe_title)s</h1>
<p class="meta">共 %(count)d 题 · %(mode)s · 姓名：____________ · 日期：____________</p>
</header>
%(body)s
<footer>anglepairs · 角的分类与计算 · eastyou</footer>
</div>
</body>
</html>
""" % {
        "title": html.escape(title),
        "safe_title": html.escape(title),
        "count": len(data),
        "mode": mode,
        "body": body,
    }
