"""anglepairs 核心逻辑测试。"""

import math
import unittest

from anglepairs.model import (
    _require_number,
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


class TestRequireNumber(unittest.TestCase):
    def test_accepts_int(self) -> None:
        self.assertEqual(_require_number(30, "角度"), 30.0)

    def test_accepts_float(self) -> None:
        self.assertAlmostEqual(_require_number(30.5, "角度"), 30.5)

    def test_accepts_zero(self) -> None:
        self.assertEqual(_require_number(0, "角度"), 0.0)

    def test_rejects_bool(self) -> None:
        with self.assertRaises(ValueError):
            _require_number(True, "角度")

    def test_rejects_string(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            _require_number("45", "角度")
        self.assertIn("角度", str(ctx.exception))

    def test_rejects_none_and_list(self) -> None:
        for value in (None, [1], {"a": 1}):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    _require_number(value, "角度")

    def test_rejects_nan_and_inf(self) -> None:
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    _require_number(value, "角度")


class TestClassifyAngle(unittest.TestCase):
    def test_zero(self) -> None:
        self.assertEqual(classify_angle(0), "零角")
        self.assertEqual(classify_angle(0.0), "零角")

    def test_acute(self) -> None:
        self.assertEqual(classify_angle(45), "锐角")
        self.assertEqual(classify_angle(89.9), "锐角")

    def test_right(self) -> None:
        self.assertEqual(classify_angle(90), "直角")
        self.assertEqual(classify_angle(90.0), "直角")

    def test_obtuse(self) -> None:
        self.assertEqual(classify_angle(120), "钝角")
        self.assertEqual(classify_angle(179.9), "钝角")

    def test_straight(self) -> None:
        self.assertEqual(classify_angle(180), "平角")

    def test_reflex(self) -> None:
        self.assertEqual(classify_angle(200), "优角")
        self.assertEqual(classify_angle(359.9), "优角")

    def test_full(self) -> None:
        self.assertEqual(classify_angle(360), "周角")

    def test_negative_raises(self) -> None:
        with self.assertRaises(ValueError):
            classify_angle(-0.5)

    def test_over_360_raises(self) -> None:
        with self.assertRaises(ValueError):
            classify_angle(360.5)

    def test_invalid_type_raises(self) -> None:
        with self.assertRaises(ValueError):
            classify_angle("90")  # type: ignore[arg-type]

    def test_nan_raises(self) -> None:
        with self.assertRaises(ValueError):
            classify_angle(math.nan)


class TestComplementSupplement(unittest.TestCase):
    def test_complement_values(self) -> None:
        self.assertAlmostEqual(complement(30), 60.0)
        self.assertAlmostEqual(complement(45), 45.0)
        self.assertAlmostEqual(complement(89.5), 0.5)

    def test_complement_invalid(self) -> None:
        for value in (0, 90, 120, -30):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    complement(value)

    def test_supplement_values(self) -> None:
        self.assertAlmostEqual(supplement(30), 150.0)
        self.assertAlmostEqual(supplement(90), 90.0)
        self.assertAlmostEqual(supplement(179.5), 0.5)

    def test_supplement_invalid(self) -> None:
        for value in (0, 180, 200, -10):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    supplement(value)


class TestTriangleAngles(unittest.TestCase):
    def test_third_angle_values(self) -> None:
        self.assertAlmostEqual(third_angle(60, 60), 60.0)
        self.assertAlmostEqual(third_angle(30, 90), 60.0)
        self.assertAlmostEqual(third_angle(1, 1), 178.0)

    def test_third_angle_rejects_non_positive(self) -> None:
        for first, second in ((0, 60), (-1, 60), (60, 0)):
            with self.subTest(first=first, second=second):
                with self.assertRaises(ValueError):
                    third_angle(first, second)

    def test_third_angle_rejects_bad_sum(self) -> None:
        for first, second in ((90, 90), (100, 90), (179, 2)):
            with self.subTest(first=first, second=second):
                with self.assertRaises(ValueError):
                    third_angle(first, second)

    def test_valid_triangle_true(self) -> None:
        self.assertTrue(is_valid_triangle_angles(60, 60, 60))
        self.assertTrue(is_valid_triangle_angles(90, 45, 45))
        self.assertTrue(is_valid_triangle_angles(30, 60, 90))
        self.assertTrue(is_valid_triangle_angles(10, 20, 150))

    def test_valid_triangle_false(self) -> None:
        self.assertFalse(is_valid_triangle_angles(60, 60, 61))
        self.assertFalse(is_valid_triangle_angles(30, 60, 89))
        self.assertFalse(is_valid_triangle_angles(90, 90, 1))

    def test_valid_triangle_tolerance(self) -> None:
        self.assertTrue(is_valid_triangle_angles(60, 60, 60.0000000001))

    def test_valid_triangle_non_positive(self) -> None:
        self.assertFalse(is_valid_triangle_angles(0, 90, 90))
        self.assertFalse(is_valid_triangle_angles(-10, 100, 90))

    def test_valid_triangle_invalid_type(self) -> None:
        with self.assertRaises(ValueError):
            is_valid_triangle_angles("60", 60, 60)  # type: ignore[arg-type]


class TestClockAngle(unittest.TestCase):
    def test_key_times(self) -> None:
        self.assertAlmostEqual(clock_angle(12, 0), 0.0)
        self.assertAlmostEqual(clock_angle(0, 0), 0.0)
        self.assertAlmostEqual(clock_angle(3, 0), 90.0)
        self.assertAlmostEqual(clock_angle(6, 0), 180.0)
        self.assertAlmostEqual(clock_angle(9, 0), 90.0)

    def test_minute_hand_offsets(self) -> None:
        self.assertAlmostEqual(clock_angle(3, 15), 7.5)
        self.assertAlmostEqual(clock_angle(12, 30), 165.0)
        self.assertAlmostEqual(clock_angle(6, 30), 15.0)

    def test_twelve_hour_cycle(self) -> None:
        self.assertAlmostEqual(clock_angle(23, 55), 27.5)
        self.assertAlmostEqual(clock_angle(11, 55), 27.5)
        self.assertAlmostEqual(clock_angle(15, 0), clock_angle(3, 0))

    def test_always_takes_smaller_angle(self) -> None:
        self.assertLessEqual(clock_angle(1, 50), 180.0)
        self.assertAlmostEqual(clock_angle(7, 5), 177.5)

    def test_hour_out_of_range(self) -> None:
        for hour in (-1, 24):
            with self.subTest(hour=hour):
                with self.assertRaises(ValueError):
                    clock_angle(hour, 0)

    def test_minute_out_of_range(self) -> None:
        for minute in (-1, 60):
            with self.subTest(minute=minute):
                with self.assertRaises(ValueError):
                    clock_angle(3, minute)

    def test_non_integer_rejected(self) -> None:
        for hour, minute in ((True, 0), (3.5, 0), (3, 15.5), ("3", "15")):
            with self.subTest(hour=hour, minute=minute):
                with self.assertRaises(ValueError):
                    clock_angle(hour, minute)  # type: ignore[arg-type]


class TestParseDms(unittest.TestCase):
    def test_plain_degrees(self) -> None:
        self.assertAlmostEqual(parse_dms("30"), 30.0)
        self.assertAlmostEqual(parse_dms("30.5"), 30.5)
        self.assertAlmostEqual(parse_dms("-12.25"), -12.25)

    def test_ascii_dms(self) -> None:
        self.assertAlmostEqual(parse_dms("30°15'30\""), 30.2583333333)

    def test_unicode_primes(self) -> None:
        self.assertAlmostEqual(parse_dms("30°15′30″"), 30.2583333333)

    def test_chinese_units(self) -> None:
        self.assertAlmostEqual(parse_dms("30度15分30秒"), 30.2583333333)
        self.assertAlmostEqual(parse_dms("12度30分"), 12.5)

    def test_spaces_and_partial(self) -> None:
        self.assertAlmostEqual(parse_dms("  45°  "), 45.0)
        self.assertAlmostEqual(parse_dms("10°20'"), 10.3333333333)
        self.assertAlmostEqual(parse_dms("10°20\"") , 10.0055555556)

    def test_negative_dms(self) -> None:
        self.assertAlmostEqual(parse_dms("-30°15'"), -30.25)

    def test_invalid_text(self) -> None:
        for text in ("", "abc", "30°15", "30'30\"", "30°15'30", "--30°"):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    parse_dms(text)

    def test_invalid_parts(self) -> None:
        for text in ("30°60'", "30°15'60\"", "30°-5'"):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    parse_dms(text)

    def test_non_string_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_dms(30)  # type: ignore[arg-type]


class TestFormatDms(unittest.TestCase):
    def test_common_values(self) -> None:
        self.assertEqual(format_dms(0), "0°00'00\"")
        self.assertEqual(format_dms(30), "30°00'00\"")
        self.assertEqual(format_dms(30.5), "30°30'00\"")
        self.assertEqual(format_dms(30.2583333333), "30°15'30\"")

    def test_carry(self) -> None:
        self.assertEqual(format_dms(59.999999), "60°00'00\"")
        self.assertEqual(format_dms(359.999999), "360°00'00\"")

    def test_negative(self) -> None:
        self.assertEqual(format_dms(-15.25), "-15°15'00\"")
        self.assertEqual(format_dms(-0.0), "0°00'00\"")

    def test_round_trip(self) -> None:
        for value in (0.0, 12.5, 30.2583333333, 89.999, 180.0):
            with self.subTest(value=value):
                self.assertAlmostEqual(
                    parse_dms(format_dms(value)), value, delta=1.0 / 3600.0
                )

    def test_invalid(self) -> None:
        for value in (math.nan, math.inf):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    format_dms(value)


class TestMakeQuiz(unittest.TestCase):
    def test_count_and_keys(self) -> None:
        items = make_quiz(12, 5)
        self.assertEqual(len(items), 12)
        for item in items:
            self.assertEqual(
                set(item), {"type", "question", "answer", "options", "explanation"}
            )
            self.assertIsInstance(item["question"], str)
            self.assertIsInstance(item["answer"], str)
            self.assertIsInstance(item["options"], list)
            self.assertIsInstance(item["explanation"], str)

    def test_options_are_four_and_unique(self) -> None:
        for item in make_quiz(20, 7):
            options = item["options"]
            self.assertIsInstance(options, list)
            self.assertEqual(len(options), 4)  # type: ignore[arg-type]
            self.assertEqual(len(set(options)), 4)  # type: ignore[arg-type]
            self.assertIn(item["answer"], options)  # type: ignore[operator]

    def test_covers_four_types(self) -> None:
        kinds = {item["type"] for item in make_quiz(10, 3)}
        self.assertGreaterEqual(len(kinds), 4)
        self.assertIn("classify", kinds)
        self.assertIn("clock", kinds)

    def test_reproducible(self) -> None:
        self.assertEqual(make_quiz(8, 42), make_quiz(8, 42))

    def test_different_seed(self) -> None:
        self.assertNotEqual(make_quiz(8, 1), make_quiz(8, 2))

    def test_zero_count(self) -> None:
        self.assertEqual(make_quiz(0, 1), [])

    def test_invalid_arguments(self) -> None:
        for count, seed in ((-1, 1), (501, 1), ("3", 1), (3, "5"), (True, 1)):
            with self.subTest(count=count, seed=seed):
                with self.assertRaises(ValueError):
                    make_quiz(count, seed)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
