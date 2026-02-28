# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run all tests
pytest unit_parser/test_units.py

# Run a single test
pytest unit_parser/test_units.py::test_feet_to_meters

# Install in editable mode
pip install -e .

# Use the CLI
convert 5 feet meters
convert 5 feet to inches
```

There is no build step; this is a pure Python package with no external runtime dependencies.

## Architecture

`unit_parser` is a dimensional-analysis library for parsing and converting physical quantities. The main class is `unit_parser` in `unit_parser/units.py`.

### Core representation

Every unit is stored in an internal dict `self._units` with two fields:

- **`signature`**: a list of integers (length 6) representing dimensional exponents — `[length, mass, time, angle, temperature, charge]`. For example, `newton` has signature `[1, 1, -2, 0, 0, 0]`.
- **`quantity`**: a float giving the conversion factor relative to the SI base unit for that dimension.

Conversion between two compatible units is `result = value * from_quantity / to_quantity`. Two units are compatible iff their signatures are equal.

### Compound unit parsing

`_signature_and_quantity_for_unit` handles underscore-separated compound unit strings such as `kilogram_meter_per_second_squared`. It splits on underscores and processes tokens left-to-right, maintaining separate numerator and denominator buffers. Special tokens:

- `per` — switches subsequent tokens to the denominator (allowed at most once)
- `squared` / `cubed` — multiply exponents and quantity of the preceding unit by 2 or 3

### Unit definition file

`unit_parser/units/units.txt` is the built-in unit database. Lines are either:

- **Signature form**: `second: [0 0 1 0 0 0]` — defines a base unit with its dimensional signature
- **Quantity form**: `minute: 60 seconds` — defines a derived unit in terms of an existing one

Custom unit files can be passed to the `unit_parser` constructor.

### Public API

All public names are re-exported from `unit_parser/__init__.py`. The key entry point is the `unit_parser` class:

```python
from unit_parser import unit_parser
up = unit_parser()
up.convert("5 feet", "meters")          # 2-arg form
up.convert(5, "feet", "meters")         # 3-arg form
up.add("3 meters", "2 feet", "meters")
up.subtract(...)
up.multiply("2 kg", "3 meter_per_second_squared", "newtons")
up.divide(...)
```

All arithmetic operations verify that the result unit's signature matches the expected signature for the operation (e.g., multiply checks that output signature equals sum of input signatures).

### CLI

`unit_parser/convert.py` defines a `main()` entry point registered as the `convert` command via `setup.py`. It accepts `convert <value> <from_unit> [to] <to_unit>`.
