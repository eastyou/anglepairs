"""anglepairs 命令行测试。"""

import contextlib
import io
import os
import tempfile
import unittest
from typing import Sequence, Tuple

from anglepairs.cli import main


def run_cli(argv: Sequence[str]) -> Tuple[int, str, str]:
    """运行命令行并捕获标准输出、标准错误与退出码。"""
    out = io.StringIO()
    err = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(argv)
        except SystemExit as exc:
            code = int(exc.code) if isinstance(exc.code, int) else 0
    return code, out.getvalue(), err.getvalue()


class TestClassifyCommand(unittest.TestCase):
    def test_acute(self) -> None:
        code, out, err = run_cli(["classify", "45"])
        self.assertEqual(code, 0)
        self.assertIn("45°", out)
        self.assertIn("锐角", out)
        self.assertEqual(err, "")

    def test_boundaries(self) -> None:
        cases = [("0", "零角"), ("90", "直角"), ("180", "平角"), ("360", "周角")]
        for value, name in cases:
            with self.subTest(value=value):
                code, out, _ = run_cli(["classify", value])
                self.assertEqual(code, 0)
                self.assertIn(name, out)

    def test_non_numeric(self) -> None:
        code, out, err = run_cli(["classify", "abc"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("错误：", err)

    def test_out_of_range(self) -> None:
        for value in ("400", "-10"):
            with self.subTest(value=value):
                code, _, err = run_cli(["classify", value])
                self.assertEqual(code, 2)
                self.assertIn("错误：", err)

    def test_nan_rejected(self) -> None:
        code, _, err = run_cli(["classify", "nan"])
        self.assertEqual(code, 2)
        self.assertIn("NaN", err)


class TestPairCommands(unittest.TestCase):
    def test_complement(self) -> None:
        code, out, _ = run_cli(["complement", "30"])
        self.assertEqual(code, 0)
        self.assertIn("60°", out)

    def test_complement_error(self) -> None:
        code, _, err = run_cli(["complement", "90"])
        self.assertEqual(code, 2)
        self.assertIn("余角", err)

    def test_supplement(self) -> None:
        code, out, _ = run_cli(["supplement", "30"])
        self.assertEqual(code, 0)
        self.assertIn("150°", out)

    def test_supplement_error(self) -> None:
        code, _, err = run_cli(["supplement", "180"])
        self.assertEqual(code, 2)
        self.assertIn("补角", err)

    def test_triangle(self) -> None:
        code, out, _ = run_cli(["triangle", "60", "60"])
        self.assertEqual(code, 0)
        self.assertIn("60°", out)

    def test_triangle_error(self) -> None:
        code, _, err = run_cli(["triangle", "100", "90"])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)


class TestClockAndDmsCommands(unittest.TestCase):
    def test_clock(self) -> None:
        code, out, _ = run_cli(["clock", "3", "0"])
        self.assertEqual(code, 0)
        self.assertIn("90°", out)
        self.assertIn("03:00", out)

    def test_clock_half_past(self) -> None:
        code, out, _ = run_cli(["clock", "12", "30"])
        self.assertEqual(code, 0)
        self.assertIn("165°", out)

    def test_clock_bad_hour(self) -> None:
        code, _, err = run_cli(["clock", "24", "0"])
        self.assertEqual(code, 2)
        self.assertIn("小时", err)

    def test_clock_bad_minute(self) -> None:
        code, _, err = run_cli(["clock", "3", "60"])
        self.assertEqual(code, 2)
        self.assertIn("分钟", err)

    def test_clock_non_integer(self) -> None:
        code, _, err = run_cli(["clock", "3.5", "0"])
        self.assertEqual(code, 2)
        self.assertIn("整数", err)

    def test_dms(self) -> None:
        code, out, _ = run_cli(["dms", "30°15'30\""])
        self.assertEqual(code, 0)
        self.assertIn("30°15'30\"", out)

    def test_dms_plain(self) -> None:
        code, out, _ = run_cli(["dms", "45.5"])
        self.assertIn("45°30'00\"", out)
        self.assertEqual(code, 0)

    def test_dms_invalid(self) -> None:
        code, _, err = run_cli(["dms", "abc"])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)


class TestQuizAndDemo(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def path(self, name: str) -> str:
        return os.path.join(self.tempdir.name, name)

    def test_quiz_creates_file(self) -> None:
        target = self.path("quiz.html")
        code, out, _ = run_cli(["quiz", "--count", "5", "--seed", "5", "-o", target])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(target))
        with open(target, encoding="utf-8") as handle:
            content = handle.read()
        self.assertIn("<!DOCTYPE html>", content)
        self.assertIn("共 5 题", content)
        self.assertIn("练习页", out)

    def test_quiz_answers(self) -> None:
        target = self.path("answers.html")
        code, _, _ = run_cli(
            ["quiz", "--count", "4", "--seed", "8", "-o", target, "--answers"]
        )
        self.assertEqual(code, 0)
        with open(target, encoding="utf-8") as handle:
            content = handle.read()
        self.assertIn("答案：", content)
        self.assertIn("解析：", content)

    def test_quiz_reproducible(self) -> None:
        first = self.path("a.html")
        second = self.path("b.html")
        run_cli(["quiz", "--count", "6", "--seed", "7", "-o", first])
        run_cli(["quiz", "--count", "6", "--seed", "7", "-o", second])
        with open(first, encoding="utf-8") as handle:
            first_text = handle.read()
        with open(second, encoding="utf-8") as handle:
            second_text = handle.read()
        self.assertEqual(first_text, second_text)

    def test_quiz_different_seed(self) -> None:
        first = self.path("c.html")
        second = self.path("d.html")
        run_cli(["quiz", "--count", "6", "--seed", "1", "-o", first])
        run_cli(["quiz", "--count", "6", "--seed", "2", "-o", second])
        with open(first, encoding="utf-8") as handle:
            first_text = handle.read()
        with open(second, encoding="utf-8") as handle:
            second_text = handle.read()
        self.assertNotEqual(first_text, second_text)

    def test_quiz_creates_parent_directory(self) -> None:
        target = os.path.join(self.tempdir.name, "nested", "quiz.html")
        code, _, _ = run_cli(["quiz", "--count", "2", "-o", target])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(target))

    def test_quiz_bad_count(self) -> None:
        for value in ("abc", "-1", "501"):
            with self.subTest(value=value):
                code, _, err = run_cli(
                    ["quiz", "--count", value, "-o", self.path("bad.html")]
                )
                self.assertEqual(code, 2)
                self.assertIn("错误：", err)

    def test_quiz_bad_seed(self) -> None:
        code, _, err = run_cli(
            ["quiz", "--seed", "x", "-o", self.path("bad.html")]
        )
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)

    def test_demo_creates_file(self) -> None:
        target = self.path("demo.html")
        code, out, _ = run_cli(["demo", "-o", target])
        self.assertEqual(code, 0)
        self.assertIn("示例练习页", out)
        with open(target, encoding="utf-8") as handle:
            content = handle.read()
        self.assertIn("共 6 题", content)
        self.assertIn("示例练习", content)


class TestParserBehaviour(unittest.TestCase):
    def test_help_exits_zero(self) -> None:
        code, out, _ = run_cli(["--help"])
        self.assertEqual(code, 0)
        self.assertIn("角的分类与计算", out)

    def test_subcommand_help(self) -> None:
        code, out, _ = run_cli(["quiz", "--help"])
        self.assertEqual(code, 0)
        self.assertIn("--answers", out)

    def test_missing_command(self) -> None:
        code, _, err = run_cli([])
        self.assertEqual(code, 2)
        self.assertIn("usage", err.lower())

    def test_unknown_command(self) -> None:
        code, _, err = run_cli(["unknown"])
        self.assertEqual(code, 2)
        self.assertIn("usage", err.lower())

    def test_demo_requires_output(self) -> None:
        code, _, _ = run_cli(["demo"])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
