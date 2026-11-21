"""anglepairs 命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from .model import (
    classify_angle,
    clock_angle,
    complement,
    format_dms,
    make_quiz,
    parse_dms,
    supplement,
    third_angle,
)
from .render import worksheet_html


def _ensure_utf8_console() -> None:
    """Windows 控制台默认编码可能无法输出中文，尽量切换为 UTF-8。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            continue


def _format_number(value: float) -> str:
    """把数字格式化成不带多余零的文本。"""
    text = "%.4f" % value
    text = text.rstrip("0").rstrip(".")
    if text in ("", "-0"):
        return "0"
    return text


def _parse_float(text: str, name: str) -> float:
    """解析命令行浮点参数，失败时给出中文提示。"""
    if not isinstance(text, str):
        raise ValueError("%s必须是数字" % name)
    try:
        return float(text.strip())
    except (TypeError, ValueError) as exc:
        raise ValueError("%s必须是数字，当前为「%s」" % (name, text)) from exc


def _parse_int(text: str, name: str) -> int:
    """解析命令行整数参数，失败时给出中文提示。"""
    if not isinstance(text, str):
        raise ValueError("%s必须是整数" % name)
    try:
        return int(text.strip())
    except (TypeError, ValueError) as exc:
        raise ValueError("%s必须是整数，当前为「%s」" % (name, text)) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="anglepairs",
        description="角的分类与计算：分类、余角补角、三角形内角、钟面夹角与度分秒",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    classify = sub.add_parser("classify", help="判断角的类型")
    classify.add_argument("degrees", help="角度，例如 45")

    comp = sub.add_parser("complement", help="求余角")
    comp.add_argument("degrees", help="角度，需满足 0 < 角 < 90")

    supp = sub.add_parser("supplement", help="求补角")
    supp.add_argument("degrees", help="角度，需满足 0 < 角 < 180")

    tri = sub.add_parser("triangle", help="已知两角求三角形第三角")
    tri.add_argument("first", help="第一个内角")
    tri.add_argument("second", help="第二个内角")

    clock = sub.add_parser("clock", help="计算钟面两针的最小夹角")
    clock.add_argument("hour", help="小时，0 到 23")
    clock.add_argument("minute", help="分钟，0 到 59")

    dms = sub.add_parser("dms", help="解析度分秒并格式化输出")
    dms.add_argument("text", help="例如 30°15'30\" 或纯度数 30.5")

    quiz = sub.add_parser("quiz", help="生成可打印的 4 选 1 练习页")
    quiz.add_argument("--count", default="10", help="题目数量，默认 10")
    quiz.add_argument("--seed", default="5", help="随机种子，默认 5")
    quiz.add_argument("-o", "--output", required=True, help="输出 HTML 路径")
    quiz.add_argument("--answers", action="store_true", help="同时输出答案与解析")

    demo = sub.add_parser("demo", help="生成固定示例练习页")
    demo.add_argument("-o", "--output", required=True, help="输出 HTML 路径")

    return parser


def _write_page(
    path_text: str,
    items: List[Dict[str, object]],
    title: str,
    show_answers: bool,
) -> Path:
    """把练习页写入指定路径，返回实际路径。"""
    output = Path(path_text)
    if output.parent and str(output.parent) not in ("", "."):
        output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(worksheet_html(items, title, show_answers), encoding="utf-8")
    return output


def _run(args: argparse.Namespace) -> int:
    if args.command == "classify":
        value = _parse_float(args.degrees, "角度")
        name = classify_angle(value)
        print("%s° 是%s" % (_format_number(value), name))
        return 0
    if args.command == "complement":
        value = _parse_float(args.degrees, "角度")
        result = complement(value)
        print("%s° 的余角是 %s°" % (_format_number(value), _format_number(result)))
        return 0
    if args.command == "supplement":
        value = _parse_float(args.degrees, "角度")
        result = supplement(value)
        print("%s° 的补角是 %s°" % (_format_number(value), _format_number(result)))
        return 0
    if args.command == "triangle":
        first = _parse_float(args.first, "第一个角")
        second = _parse_float(args.second, "第二个角")
        result = third_angle(first, second)
        print(
            "已知 %s° 和 %s°，第三个内角是 %s°"
            % (_format_number(first), _format_number(second), _format_number(result))
        )
        return 0
    if args.command == "clock":
        hour = _parse_int(args.hour, "小时")
        minute = _parse_int(args.minute, "分钟")
        angle = clock_angle(hour, minute)
        print(
            "%02d:%02d 时，时针与分针的最小夹角是 %s°"
            % (hour, minute, _format_number(angle))
        )
        return 0
    if args.command == "dms":
        value = parse_dms(args.text)
        print(
            "%s = %s（%s°）"
            % (args.text, format_dms(value), _format_number(value))
        )
        return 0
    if args.command == "quiz":
        count = _parse_int(args.count, "题目数量")
        seed = _parse_int(args.seed, "随机种子")
        items = make_quiz(count, seed)
        output = _write_page(
            args.output, items, "角的分类与计算 · 随堂练习", bool(args.answers)
        )
        print("已生成%s：%s" % ("答案页" if args.answers else "练习页", output))
        return 0
    if args.command == "demo":
        items = make_quiz(6, 2026)
        output = _write_page(args.output, items, "角的分类与计算 · 示例练习", False)
        print("已生成示例练习页：%s" % output)
        return 0
    raise ValueError("未知命令：%s" % args.command)


def main(argv: Optional[Sequence[str]] = None) -> int:
    _ensure_utf8_console()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return _run(args)
    except (TypeError, ValueError) as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
