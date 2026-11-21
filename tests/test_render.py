"""anglepairs 渲染层测试。"""

import math
import unittest

from anglepairs.render import angle_svg, worksheet_html


def make_item(question: str = "示例题目") -> dict:
    return {
        "question": question,
        "answer": "锐角",
        "options": ["锐角", "钝角", "直角", "平角"],
        "explanation": "0° < 角 < 90°。",
    }


class TestAngleSvg(unittest.TestCase):
    def test_returns_svg_document(self) -> None:
        svg = angle_svg(45)
        self.assertIn("<svg", svg)
        self.assertIn("</svg>", svg)
        self.assertIn('role="img"', svg)

    def test_acute_has_arc(self) -> None:
        self.assertIn("<path", angle_svg(45))

    def test_zero_has_no_arc(self) -> None:
        self.assertNotIn("<path", angle_svg(0))

    def test_right_angle_label(self) -> None:
        svg = angle_svg(90)
        self.assertIn("90°", svg)
        self.assertIn("直角", svg)

    def test_straight_and_reflex(self) -> None:
        self.assertIn("平角", angle_svg(180))
        self.assertIn("优角", angle_svg(270))

    def test_full_angle_uses_circle(self) -> None:
        svg = angle_svg(360)
        self.assertEqual(svg.count("<circle"), 2)
        self.assertIn("周角", svg)

    def test_invalid_angles(self) -> None:
        for value in (-1, 360.5, math.nan, math.inf):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    angle_svg(value)

    def test_invalid_type(self) -> None:
        with self.assertRaises(ValueError):
            angle_svg("45")  # type: ignore[arg-type]


class TestWorksheetHtml(unittest.TestCase):
    def test_basic_structure(self) -> None:
        html = worksheet_html([make_item()], "角的练习")
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("角的练习", html)
        self.assertIn("共 1 题", html)

    def test_options_rendered(self) -> None:
        html = worksheet_html([make_item("第一题")], "练习")
        for option in ("锐角", "钝角", "直角", "平角"):
            self.assertIn(option, html)
        self.assertIn('class="tag">A</span>', html)
        self.assertIn('class="tag">D</span>', html)

    def test_answers_hidden_by_default(self) -> None:
        html = worksheet_html([make_item()], "练习")
        self.assertNotIn("解析：", html)
        self.assertNotIn("答案：", html)
        self.assertIn("答：", html)

    def test_answers_visible(self) -> None:
        html = worksheet_html([make_item()], "练习", show_answers=True)
        self.assertIn("答案：", html)
        self.assertIn("解析：", html)
        self.assertIn('class="correct"', html)

    def test_escaping(self) -> None:
        html = worksheet_html([make_item("<script>alert(1)</script>")], "<b>标题</b>")
        self.assertNotIn("<script>", html)
        self.assertNotIn("<b>标题</b>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&lt;b&gt;", html)

    def test_empty_items(self) -> None:
        html = worksheet_html([], "空练习")
        self.assertIn("共 0 题", html)

    def test_invalid_items_container(self) -> None:
        with self.assertRaises(TypeError):
            worksheet_html({"question": "x"}, "标题")  # type: ignore[arg-type]

    def test_missing_field(self) -> None:
        broken = make_item()
        del broken["explanation"]
        with self.assertRaises(ValueError):
            worksheet_html([broken], "标题")

    def test_wrong_option_count(self) -> None:
        broken = make_item()
        broken["options"] = ["A", "B", "C"]
        with self.assertRaises(ValueError):
            worksheet_html([broken], "标题")

    def test_answer_not_in_options(self) -> None:
        broken = make_item()
        broken["answer"] = "未知"
        with self.assertRaises(ValueError):
            worksheet_html([broken], "标题")

    def test_invalid_title_and_flag(self) -> None:
        with self.assertRaises(ValueError):
            worksheet_html([make_item()], "")
        with self.assertRaises(ValueError):
            worksheet_html([make_item()], "标题", show_answers="yes")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
