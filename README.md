# anglepairs

[![CI](https://github.com/eastyou/anglepairs/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/anglepairs/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

面向课堂的角的分类与计算工具：判断角的类型、求余角与补角、补全三角形内角、计算钟面夹角、转换度分秒，并生成可打印的练习页。

## 功能

- 按度数判断零角、锐角、直角、钝角、平角、优角、周角
- 求余角与补角，并严格校验角度范围
- 已知两个内角求三角形第三角，判断三角是否合法
- 计算钟面时针与分针的最小夹角，支持 12 小时循环
- 解析与格式化度分秒，自动处理进位和浮点误差
- 按随机种子生成可复现的 4 选 1 练习，覆盖 5 种题型
- 生成含内联 CSS 的自包含练习页或答案页，可直接打印
- 纯 Python 标准库，零第三方依赖

## 安装

```bash
pip install -e .
```

也可以不安装，直接在仓库根目录运行 `python -m anglepairs`。

## 使用

```bash
# 判断角的类型
anglepairs classify 120        # 120° 是钝角
anglepairs classify 90         # 90° 是直角

# 余角与补角
anglepairs complement 35       # 35° 的余角是 55°
anglepairs supplement 35       # 35° 的补角是 145°

# 三角形第三角
anglepairs triangle 60 60      # 已知 60° 和 60°，第三个内角是 60°

# 钟面夹角
anglepairs clock 3 15          # 03:15 时，时针与分针的最小夹角是 7.5°

# 度分秒
anglepairs dms "30°15'30\""    # 30°15'30" = 30°15'30"（30.2583°）

# 生成练习页与答案页
anglepairs quiz --count 10 --seed 5 -o examples/angles.html
anglepairs quiz --count 10 --seed 5 -o examples/answers.html --answers

# 生成固定示例页
anglepairs demo -o examples/angles.html
```

## 作为库使用

```python
from anglepairs import (
    classify_angle,
    clock_angle,
    complement,
    format_dms,
    make_quiz,
    parse_dms,
    third_angle,
)

assert classify_angle(120) == "钝角"
assert complement(30) == 60
assert third_angle(30, 90) == 60
assert clock_angle(3, 15) == 7.5
assert abs(parse_dms("30°15'30\"") - 30.2583333333) < 1e-6
assert format_dms(30.2583333333) == "30°15'30\""
assert len(make_quiz(10, 5)) == 10
```

## 示例

[examples/angles.html](examples/angles.html) 是生成的练习页，包含 5 种题型、4 个选项与打印样式，直接用浏览器打开即可打印。

## 测试

```bash
python -m unittest discover -s tests -v
```

共 109 项单元测试，覆盖分类边界（0、90、180、360）、余角补角、三角形内角、钟面夹角、度分秒往返、练习生成、HTML 转义与命令行退出码。CI 在 Linux、macOS、Windows 上运行 Python 3.9 ~ 3.13。

## 许可

MIT © 2026 eastyou
