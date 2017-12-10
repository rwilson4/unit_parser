from .units import unit_parser
import pytest

def inc(x):
    return x + 1

def test_feet_to_meters():
    """Tests conversion from feet to meters.

    """
    up = unit_parser()
    assert up.convert("5 feet", "meters") == 1.524


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


def test_meters_divided_by_seconds():
    """Tests dividing meters by seconds.

    """
    up = unit_parser()
    assert up.divide("5 meters", "2 seconds", "meters_per_second") == 2.5


def test_meters_plus_meters():
    """Tests adding meters

    """
    up = unit_parser()
    assert up.add("5 meters", "2 meters", "meters") == 7


def test_meters_plus_seconds():
    """Tests adding meters

    """
    up = unit_parser()
    with pytest.raises(ValueError):
        up.add("5 meters", "2 seconds", "meters")
