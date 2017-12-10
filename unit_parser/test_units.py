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
        assert up.convert("5 feet", "lbf")


    
