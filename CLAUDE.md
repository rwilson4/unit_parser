# CLAUDE.md

Guidance for Claude Code (claude.ai/code) when working in this repository.

This file is the single source of truth for project conventions. The README is
written for end users; this file is written for contributors (human or agent).

## What this library is

`unit_parser` is a small, dependency-free dimensional-analysis library. Its
distinguishing feature is that **units are parsed from strings**, including
compound units like `kilogram_meter_per_second_squared`. The original use case
was parsing free-form physical quantities out of plain-text input files (JSON
configs, etc.) without forcing the author to commit to one system of
measurement — if a user wants to specify a distance in furlongs, the library
can accept it.

## Commands

```bash
# Run all tests
pytest unit_parser/test_units.py

# Run a single test
pytest unit_parser/test_units.py::test_feet_to_meters

# Install in editable mode
pip install -e .

# CLI
convert 5 feet meters
convert 5 feet to inches   # the "to" filler word is accepted
```

There is no build step and no runtime dependencies.

## Modernization roadmap

The codebase predates current Python packaging conventions and is mid-cleanup.
Treat the following as the **target state** when making changes — prefer to
move the code toward this state rather than entrench what exists today.

| Area              | Status                           |
| ----------------- | -------------------------------- |
| Python version    | Done — `requires-python = ">=3.11"` in `pyproject.toml` |
| Dependency mgmt   | Done — `uv` + `uv.lock`; dev deps in `[dependency-groups]` |
| Linting           | Done — `ruff` (lint + format), single-quote style |
| Type checking     | Done — `mypy --strict`; pyre headers removed |
| CI                | Done — GitHub Actions on 3.11/3.12/3.13 (`.github/workflows/ci.yml`) |
| Packaging         | Done — PEP 621 only; `MANIFEST.in` and `requirements.txt` deleted |
| Tests             | TODO — move to `tests/`; add coverage threshold |
| Class naming      | Done — `README.md` updated to `UnitParser`; CI badge points at GitHub Actions |

Local commands:

```bash
uv sync                # install dev deps + editable install
uv run pytest          # tests
uv run ruff check .    # lint
uv run ruff format .   # format
uv run mypy            # type-check
```

Don't introduce a runtime dependency just to satisfy a lint rule; the
zero-dependency property is a feature.

## Architecture

Everything lives in `unit_parser/units.py`. The package is small enough that a
single-module layout is correct — resist splitting it up prematurely.

### Core representation

Each unit is stored in `UnitParser._units` as a `_UnitSpec` dataclass with two
fields:

- **`signature`**: tuple of integers (length 6 by default) holding dimensional
  exponents in the order `[length, mass, time, angle, temperature, charge]`.
  Example: `newton` is `(1, 1, -2, 0, 0, 0)`.
- **`quantity`**: float conversion factor relative to the SI base unit for
  that dimension.

Conversion between two compatible units is `value * from.quantity /
to.quantity`. Two units are *compatible* iff their signatures are equal.

The signature length is **not hardcoded to 6** — it is set by the first
signature-form line encountered in the unit file (`self._sig_len`). All
subsequent signature-form lines must agree. A custom unit file can therefore
use any consistent dimension count.

Both `_UnitSpec` fields are immutable, so the cache lookup in
`_signature_and_quantity_for_unit` returns the stored spec directly without
defensive copying. Anything that needs to mutate (the per-call accumulators
inside that method) builds its own local `list[int]` and packages the result
back into a `tuple` before returning.

### Compound unit parsing (`_signature_and_quantity_for_unit`)

Splits the input on `_` and walks tokens left-to-right, maintaining `signature`
/ `quantity` accumulators plus a `sig_buffer` / `quantity_buffer` holding the
*most recently seen unit token* (so that `squared` / `cubed` can re-apply it).

Special tokens:

- `per` — switches subsequent tokens to the denominator. **Allowed at most
  once** per specification.
- `squared` — re-applies the previous unit token once more (so `meter_squared`
  contributes the meter exponent twice).
- `cubed` — re-applies it twice more. Implemented by doubling `sig_buffer` and
  squaring `quantity_buffer` before merging, so that `unit + 2*unit = 3*unit`.
  Be careful when refactoring: if you change the order of "merge buffer into
  accumulator" vs. "scale buffer", you will silently get the wrong exponent.
- `squared`/`cubed` cannot follow `per` directly or another modifier
  (`squared_squared` is rejected).

`squared`/`cubed` bind only to the immediately preceding token —
`second_meter_squared` means "second times meter²", not "(second·meter)²". For
the latter, write `second_squared_meter_squared`.

### Unit definition file (`unit_parser/units/units.txt`)

Two line forms:

- **Signature form**: `second: [0 0 1 0 0 0]` — defines a base unit with
  implicit quantity 1.0.
- **Quantity form**: `minute: 60 seconds` — defines a derived unit in terms of
  any previously-defined unit (or compound expression).

`#` introduces a comment. Custom unit files can be passed to the
`UnitParser(unit_definitions=...)` constructor.

#### Known data-file quirks (worth fixing during modernization)

These are not bugs in the parser — they're choices in `units.txt`:

- `teaspoon: 0.3333333 tablespoons` — should be exactly 1/3. Consider allowing
  rational expressions in the quantity form, or just use more digits.
- `year: 365 days` — uses the common-year convention, not Julian (365.25).
  Document the choice or change it.
- `degF: 0.5555555555555 degC` — temperature **differences** only. No offset
  is supported anywhere in the code, so converting an absolute temperature
  through this unit will produce nonsense. Document this loudly, or extend
  `_UnitSpec` with an offset and teach `convert` to refuse mixing absolute and
  relative temperatures.
- Aliases like `seconds: 1 second` are how plurals/abbreviations work — there
  is no built-in plural handling.

### Public API

Re-exported from `unit_parser/__init__.py`:

```python
from unit_parser import UnitParser
up = UnitParser()
up.convert("5 feet", "meters")          # 2-arg form
up.convert(5, "feet", "meters")         # 3-arg form
up.add("3 meters", "2 feet", "meters")
up.subtract("3 meters", "2 feet", "meters")
up.multiply("2 kg", "3 meter_per_second_squared", "newtons")
up.divide("10 meters", "2 seconds", "meter_per_second")
```

Every arithmetic method takes the **desired result units** as its last
argument and validates that the dimensional signature of the result matches
that unit. Mismatches raise `ValueError` — they don't silently coerce.

`convert` uses `*args: str | float` to accept both 2-arg and 3-arg forms. When
modernizing, replace this with `@typing.overload` so callers get accurate
types.

### CLI (`unit_parser/convert.py`)

Registered as the `convert` console script via `pyproject.toml`. Accepts:

```
convert <value> <from_unit> [to] <to_unit>
```

Implementation note: when more than one trailing positional is supplied, the
code currently picks `args.desired_units[1]` and discards everything else
without validating that the first filler word is `"to"`. `convert 5 feet
banana meters` parses as `5 feet → meters` with no warning. A proper rewrite
should explicitly accept an optional `to` literal.

## Conventions

- **No new runtime dependencies.** Test/dev dependencies are fine; runtime
  deps are not.
- **Public surface = `unit_parser/__init__.py`.** Anything not re-exported
  there is private and may change without notice. Tests reach into `_`-prefixed
  methods on purpose; new external callers should not.
- **Errors are `ValueError`.** Don't introduce custom exception types unless
  there's a real need to discriminate them at a call site.
- **String quoting**: existing code uses single quotes. Ruff's default is
  double quotes — pick one in `pyproject.toml` and let the formatter enforce
  it; don't mix.
- **Docstrings** are NumPy-style. Keep that consistent if you add new ones.
- **Don't write throwaway planning docs.** Work from this file and the code.

## Test coverage gaps

The current suite (`unit_parser/test_units.py`) is a good starting point but
misses:

- `cubed` keyword (only `squared` is exercised)
- Successfully loading a *valid* custom unit file (only error paths are tested)
- Compound units defined inside a custom unit file
- `_parse_physical_quantity` happy path (only the error case is tested
  directly; happy path is covered transitively)
- Round-trip conversions (`A→B→A` should equal the input within tolerance)
- Whitespace / case sensitivity behavior at boundaries

When adding tests, prefer `pytest.approx` over exact float equality for any
conversion that goes through more than one multiplication.
