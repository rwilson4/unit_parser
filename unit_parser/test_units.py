from .units import unit_parser
import pytest
import os

#   File: test_units.py
#   Purpose: test cases for unit parser
#
#   Copyright 2017 Bob Wilson
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


def get_cwd():
    this_dir, this_filename = os.path.split(__file__)
    return this_dir


def test_feet_to_meters():
    """Tests conversion from feet to meters, using 2 arguments.

    """
    up = unit_parser()
    assert up.convert("5 feet", "meters") == 1.524


def test_feet_to_meters_long():
    """Tests conversion from feet to meters, using 3 arguments.

    """
    up = unit_parser()
    assert up.convert(5, "feet", "meters") == 1.524


def test_days_to_seconds():
    """Tests conversion from days to seconds.

    """
    up = unit_parser()
    assert up.convert("1 day", "seconds") == 86400


def test_years_to_minutes():
    """Tests conversion from years to minutes.

    """
    up = unit_parser()
    assert up.convert("1 year", "minutes") == 525600


def test_lbf_to_newton():
    """Tests conversion from years to minutes.

    """
    up = unit_parser()
    assert up.convert("1 lbf", "newtons") == pytest.approx(4.44822)


def test_feet_to_lbf():
    """Tests conversion from feet to lbf (expect error).

    """
    up = unit_parser()
    with pytest.raises(ValueError):
        up.convert("5 feet", "lbf")


def test_kg_times_meters_per_second_squared():
    """Tests multiplying kilograms and meters_per_second_squared.

    """
    up = unit_parser()
    assert up.multiply("2 kilograms", "5 meters_per_second_squared", "newtons") == 10


def test_kg_times_meters_per_second_squared_in_slugs():
    """Tests multiplying kilograms and meters_per_second_squared.

    """
    up = unit_parser()
    with pytest.raises(ValueError):
        up.multiply("2 kilograms", "5 meters_per_second_squared", "slug")


def test_meters_divided_by_seconds():
    """Tests dividing meters by seconds.

    """
    up = unit_parser()
    assert up.divide("5 meters", "2 seconds", "meters_per_second") == 2.5


def test_meters_divided_by_seconds_in_yards():
    """Tests dividing meters by seconds but expressing the results in yards.

    """
    up = unit_parser()
    with pytest.raises(ValueError):
        up.divide("5 meters", "2 seconds", "yards")


def test_meters_plus_meters():
    """Tests adding meters.

    """
    up = unit_parser()
    assert up.add("5 meters", "2 meters", "meters") == 7


def test_meters_plus_seconds():
    """Tests adding meters and seconds.

    """
    up = unit_parser()
    with pytest.raises(ValueError):
        up.add("5 meters", "2 seconds", "meters")

def test_meters_plus_meters_in_seconds():
    """Tests adding meters and meters but expressing results in seconds.

    """
    up = unit_parser()
    with pytest.raises(ValueError):
        up.add("5 meters", "2 meters", "seconds")

def test_meters_minus_meters():
    """Tests subtracting meters.

    """
    up = unit_parser()
    assert up.subtract("5 meters", "2 meters", "meters") == 3


def test_meters_minus_seconds():
    """Tests subtracting meters minus seconds.

    """
    up = unit_parser()
    with pytest.raises(ValueError):
        up.subtract("5 meters", "2 seconds", "meters")


def test_meters_minus_meters_in_seconds():
    """Tests subtracting meters minus meters in seconds.

    """
    up = unit_parser()
    with pytest.raises(ValueError):
        up.subtract("5 meters", "2 meters", "seconds")


def test_invalid_physical_quantity():
    """Tests attempting to parse an invalid physical quantity.

    """
    up = unit_parser()
    with pytest.raises(SyntaxError):
        up._parse_physical_quantity("meters")


def test_per_per_unit_specification():
    """Tests attempting to parse a unit specification 'per_per'.

    """
    up = unit_parser()
    with pytest.raises(SyntaxError):
        up._signature_and_quantity_for_unit("per_per")


def test_squared_unit_specification():
    """Tests attempting to parse a unit specification 'squared'.

    """
    up = unit_parser()
    with pytest.raises(SyntaxError):
        up._signature_and_quantity_for_unit("squared")


def test_unit_specification_typo():
    """Tests attempting to parse a unit specification 'metes'.

    """
    up = unit_parser()
    with pytest.raises(SyntaxError):
        up._signature_and_quantity_for_unit("metes")


def test_invalid_unit_spec_just_key():
    """Tests a unit specification file with just a key (no value).

    """
    this_dir = get_cwd()
    path = os.path.join(this_dir, "test_files", "just_key.txt")
    with pytest.raises(SyntaxError):
        up = unit_parser(path)


def test_invalid_unit_spec_duplicate_entry():
    """Tests a unit specification file with the same unit defined twice.

    """
    this_dir = get_cwd()
    path = os.path.join(this_dir, "test_files", "duplicate_entry.txt")
    with pytest.raises(SyntaxError):
        up = unit_parser(path)


def test_invalid_unit_spec_nonalphabetic_unit_name():
    """Tests a unit specification file with a unit name 's3cond'.

    """
    this_dir = get_cwd()
    path = os.path.join(this_dir, "test_files", "non_alphabetic_unit_name.txt")
    with pytest.raises(SyntaxError):
        up = unit_parser(path)


def test_invalid_unit_spec_inconsistent_signature_lengths():
    """Tests a unit specification file with inconsistent signature
    lengths.

    """
    this_dir = get_cwd()
    path = os.path.join(this_dir, "test_files", "different_signature_lengths.txt")
    with pytest.raises(SyntaxError):
        up = unit_parser(path)


def test_invalid_unit_spec_negative_quantity():
    """Tests a unit specification file with negative quantity.

    """
    this_dir = get_cwd()
    path = os.path.join(this_dir, "test_files", "negative_quantity.txt")
    with pytest.raises(SyntaxError):
        up = unit_parser(path)
