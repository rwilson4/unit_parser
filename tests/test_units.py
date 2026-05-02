"""Tests for unit_parser."""

import os
import sys
from unittest.mock import patch

import pytest

from unit_parser.convert import main as convert_main
from unit_parser.units import UnitParser


def get_cwd() -> str:
    this_dir, this_filename = os.path.split(__file__)
    return this_dir


def test_feet_to_meters():
    """Tests conversion from feet to meters, using 2 arguments."""
    up = UnitParser()
    assert up.convert('5 feet', 'meters') == 1.524


def test_feet_to_meters_long():
    """Tests conversion from feet to meters, using 3 arguments."""
    up = UnitParser()
    assert up.convert(5, 'feet', 'meters') == 1.524


def test_days_to_seconds():
    """Tests conversion from days to seconds."""
    up = UnitParser()
    assert up.convert('1 day', 'seconds') == 86400


def test_years_to_minutes():
    """Tests conversion from years to minutes."""
    up = UnitParser()
    assert up.convert('1 year', 'minutes') == 525600


def test_lbf_to_newton():
    """Tests conversion from years to minutes."""
    up = UnitParser()
    assert up.convert('1 lbf', 'newtons') == pytest.approx(4.44822)


def test_feet_to_lbf():
    """Tests conversion from feet to lbf (expect error)."""
    up = UnitParser()
    with pytest.raises(ValueError):
        up.convert('5 feet', 'lbf')


def test_kg_times_meters_per_second_squared():
    """Tests multiplying kilograms and meters_per_second_squared."""
    up = UnitParser()
    assert up.multiply('2 kilograms', '5 meters_per_second_squared', 'newtons') == 10


def test_kg_times_meters_per_second_squared_in_slugs():
    """Tests multiplying kilograms and meters_per_second_squared."""
    up = UnitParser()
    with pytest.raises(ValueError):
        up.multiply('2 kilograms', '5 meters_per_second_squared', 'slug')


def test_meters_divided_by_seconds():
    """Tests dividing meters by seconds."""
    up = UnitParser()
    assert up.divide('5 meters', '2 seconds', 'meters_per_second') == 2.5


def test_meters_divided_by_seconds_in_yards():
    """Tests dividing meters by seconds but expressing the results in yards."""
    up = UnitParser()
    with pytest.raises(ValueError):
        up.divide('5 meters', '2 seconds', 'yards')


def test_meters_plus_meters():
    """Tests adding meters."""
    up = UnitParser()
    assert up.add('5 meters', '2 meters', 'meters') == 7


def test_meters_plus_seconds():
    """Tests adding meters and seconds."""
    up = UnitParser()
    with pytest.raises(ValueError):
        up.add('5 meters', '2 seconds', 'meters')


def test_meters_plus_meters_in_seconds():
    """Tests adding meters and meters but expressing results in seconds."""
    up = UnitParser()
    with pytest.raises(ValueError):
        up.add('5 meters', '2 meters', 'seconds')


def test_meters_minus_meters():
    """Tests subtracting meters."""
    up = UnitParser()
    assert up.subtract('5 meters', '2 meters', 'meters') == 3


def test_meters_minus_seconds():
    """Tests subtracting meters minus seconds."""
    up = UnitParser()
    with pytest.raises(ValueError):
        up.subtract('5 meters', '2 seconds', 'meters')


def test_meters_minus_meters_in_seconds():
    """Tests subtracting meters minus meters in seconds."""
    up = UnitParser()
    with pytest.raises(ValueError):
        up.subtract('5 meters', '2 meters', 'seconds')


def test_invalid_physical_quantity():
    """Tests attempting to parse an invalid physical quantity."""
    up = UnitParser()
    with pytest.raises(ValueError):
        up._parse_physical_quantity('meters')


def test_per_per_unit_specification():
    """Tests attempting to parse a unit specification 'per_per'."""
    up = UnitParser()
    with pytest.raises(ValueError):
        up._signature_and_quantity_for_unit('per_per')


def test_squared_unit_specification():
    """Tests attempting to parse a unit specification 'squared'."""
    up = UnitParser()
    with pytest.raises(ValueError):
        up._signature_and_quantity_for_unit('squared')


def test_unit_specification_typo():
    """Tests attempting to parse a unit specification 'metes'."""
    up = UnitParser()
    with pytest.raises(ValueError):
        up._signature_and_quantity_for_unit('metes')


def test_invalid_unit_spec_just_key():
    """Tests a unit specification file with just a key (no value)."""
    this_dir = get_cwd()
    path = os.path.join(this_dir, 'test_files', 'just_key.txt')
    with pytest.raises(ValueError):
        UnitParser(path)


def test_invalid_unit_spec_duplicate_entry():
    """Tests a unit specification file with the same unit defined twice."""
    this_dir = get_cwd()
    path = os.path.join(this_dir, 'test_files', 'duplicate_entry.txt')
    with pytest.raises(ValueError):
        UnitParser(path)


def test_invalid_unit_spec_nonalphabetic_unit_name():
    """Tests a unit specification file with a unit name 's3cond'."""
    this_dir = get_cwd()
    path = os.path.join(this_dir, 'test_files', 'non_alphabetic_unit_name.txt')
    with pytest.raises(ValueError):
        UnitParser(path)


def test_invalid_unit_spec_inconsistent_signature_lengths():
    """Tests a unit specification file with inconsistent signature
    lengths.

    """
    this_dir = get_cwd()
    path = os.path.join(this_dir, 'test_files', 'different_signature_lengths.txt')
    with pytest.raises(ValueError):
        UnitParser(path)


def test_invalid_unit_spec_negative_quantity():
    """Tests a unit specification file with negative quantity."""
    this_dir = get_cwd()
    path = os.path.join(this_dir, 'test_files', 'negative_quantity.txt')
    with pytest.raises(ValueError):
        UnitParser(path)


def test_invalid_num_args():
    up = UnitParser()
    with pytest.raises(TypeError):
        up.convert(5, 'feet', 'to', 'meters')  # type: ignore[call-overload]


def test_invalid_convert_args():
    up = UnitParser()
    with pytest.raises(ValueError):
        up.convert('cat', 'feet', 'meters')  # type: ignore[call-overload]


def test_convert_two_arg_form_requires_string():
    """The 2-arg form parses '5 feet' from a string; passing a number
    instead is rejected at runtime even when overload checking is bypassed.

    """
    up = UnitParser()
    with pytest.raises(ValueError):
        up.convert(5, 'feet')  # type: ignore[call-overload]


def test_command_line_convert(capsys: pytest.CaptureFixture[str]) -> None:
    testargs = ['convert', '5', 'feet', 'inches']
    with patch.object(sys, 'argv', testargs):
        convert_main()
    assert float(capsys.readouterr().out.strip()) == pytest.approx(60)


def test_command_line_convert_with_to(capsys: pytest.CaptureFixture[str]) -> None:
    testargs = ['convert', '5', 'feet', 'to', 'inches']
    with patch.object(sys, 'argv', testargs):
        convert_main()
    assert float(capsys.readouterr().out.strip()) == pytest.approx(60)


def test_command_line_convert_invalid_filler():
    """CLI should reject a filler word other than 'to' instead of silently
    dropping arguments.

    """
    testargs = ['convert', '5', 'feet', 'banana', 'inches']
    with patch.object(sys, 'argv', testargs):
        with pytest.raises(SystemExit):
            convert_main()


# --- cubed keyword -----------------------------------------------------------


def test_cubed_volume_conversion():
    """`meter_cubed` is volume; 1 m^3 = 1000 liters."""
    up = UnitParser()
    assert up.convert('1 meter_cubed', 'liters') == pytest.approx(1000)


def test_cubed_signature_exponent():
    """`cubed` should contribute exponent 3, not 2 -- guard against the
    buffer-doubling logic going subtly wrong.

    """
    up = UnitParser()
    spec = up._signature_and_quantity_for_unit('meter_cubed')
    # length exponent is the first slot; everything else zero.
    assert spec.signature[0] == 3
    assert spec.signature[1:] == (0, 0, 0, 0, 0)


def test_cubed_in_denominator():
    """`per X_cubed` should subtract 3 from the relevant exponent."""
    up = UnitParser()
    # kg / m^3 has signature [-3, 1, 0, 0, 0, 0]
    spec = up._signature_and_quantity_for_unit('kilogram_per_meter_cubed')
    assert spec.signature == (-3, 1, 0, 0, 0, 0)


# --- custom unit file (happy path) -------------------------------------------


def test_load_valid_custom_unit_file():
    """Loading a valid custom file should populate units defined by both
    signature and quantity forms, including compound expressions.

    """
    path = os.path.join(get_cwd(), 'test_files', 'valid_custom.txt')
    up = UnitParser(path)
    assert up.convert('1 km', 'm') == pytest.approx(1000)
    assert up.convert('1 hr', 'sec') == pytest.approx(3600)


def test_custom_unit_file_compound_definition():
    """A unit defined by a compound expression (`mps: 1 m_per_sec`) should
    have the right derived signature and quantity.

    """
    path = os.path.join(get_cwd(), 'test_files', 'valid_custom.txt')
    up = UnitParser(path)
    # 1 m/s = 3.6 km/hr
    assert up.convert('1 mps', 'km_per_hr') == pytest.approx(3.6)


def test_custom_unit_file_uses_its_own_dimension_count():
    """The fixture file declares 2 dimensions; the parser should adopt that,
    not the default 6.

    """
    path = os.path.join(get_cwd(), 'test_files', 'valid_custom.txt')
    up = UnitParser(path)
    assert up._sig_len == 2


# --- _parse_physical_quantity (happy path) -----------------------------------


def test_parse_physical_quantity_simple():
    up = UnitParser()
    qty, units = up._parse_physical_quantity('5 feet')
    assert qty == 5.0
    assert units == 'feet'


def test_parse_physical_quantity_decimal():
    up = UnitParser()
    qty, units = up._parse_physical_quantity('3.14 meters')
    assert qty == pytest.approx(3.14)
    assert units == 'meters'


def test_parse_physical_quantity_no_space():
    """The number-units regex uses \\s*, so '5feet' is accepted."""
    up = UnitParser()
    qty, units = up._parse_physical_quantity('5feet')
    assert qty == 5.0
    assert units == 'feet'


def test_parse_physical_quantity_compound_units():
    up = UnitParser()
    qty, units = up._parse_physical_quantity('88 miles_per_hour')
    assert qty == 88.0
    assert units == 'miles_per_hour'


# --- round-trip conversions --------------------------------------------------


@pytest.mark.parametrize(
    ('value', 'unit_a', 'unit_b'),
    [
        (7.3, 'feet', 'meters'),
        (42.0, 'kilograms', 'lbm'),
        (1.5, 'liters', 'gallons'),
        (88.0, 'miles_per_hour', 'meter_per_second'),
        (1.0, 'newton', 'lbf'),
    ],
)
def test_round_trip(value, unit_a, unit_b):
    """`A -> B -> A` should recover the original within float tolerance."""
    up = UnitParser()
    intermediate = up.convert(value, unit_a, unit_b)
    final = up.convert(intermediate, unit_b, unit_a)
    assert final == pytest.approx(value)


# --- case sensitivity --------------------------------------------------------


def test_unit_lookup_is_case_sensitive():
    """`Feet` is not registered as an alias for `feet`."""
    up = UnitParser()
    with pytest.raises(ValueError):
        up.convert('5 Feet', 'meters')
