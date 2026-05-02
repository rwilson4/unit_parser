"""Unit parsing and conversion."""

import re
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import overload


@dataclass(frozen=True)
class _UnitSpec:
    """Internal representation of a unit's dimensional signature and quantity."""

    signature: tuple[int, ...]
    quantity: float


class UnitParser:
    """Unit Parser and Conversions.

    This library allows for converting between units. Perhaps its most
    interesting feature is its flexible unit specification
    parsing. Units may be specified by a definition file which
    accompanies this library, or by combinations of units defined in
    that file.

    For example, if 'second', 'meter', and 'kilogram' are defined by
    the file, the specification 'kilogram_meter_per_second_squared' is
    valid and parsed as expected. These compound specifications
    consist of tokens separated by underscores. Tokens include
    previously defined units like 'kilogram' as well as the special
    keywords 'per', 'squared', and 'cubed'.

    The keyword 'per' may be used at most once per specification and
    directs that all subsequent tokens belong in the denominator of
    the unit.

    The keywords 'squared' and 'cubed' indicate that the preceding
    token should be repeated once or twice more, respectively. They
    cannot be daisy chained, for example: 'meters_squared_squared' is
    not permitted, but 'meters_squared_meters_squared' or
    'meters_cubed_meters' would be. They also only apply to the
    preceding token, so 'second_second_meter_meter' is equivalent to
    'second_squared_meter_squared' but not 'second_meter_squared'.

    Finally, 'second', 'seconds', and 'sec' are not automatically
    treated as equivalent units, but the unit definition file can and
    does create these as if they were aliases. For example, 'seconds'
    is defined as '1 second'.

    """

    def __init__(self, unit_definitions: str | Path | None = None) -> None:
        self._units: dict[str, _UnitSpec] = {}
        self._sig_len: int = -1
        if unit_definitions is not None:
            self._parse_unit_file(unit_definitions)
        else:
            unit_path = Path(__file__).parent / 'units' / 'units.txt'
            self._parse_unit_file(unit_path)

    def _signature_and_quantity_for_unit(self, unit: str) -> _UnitSpec:
        """Parse unit specification.

        Parameters
        ----------
        unit : str
            String representing a unit, like
            "meters_per_second_squared".

        Returns
        -------
        _UnitSpec
            The signature and quantity for the unit.

        """
        if unit in self._units:
            return self._units[unit]

        # Parse string
        tokens = unit.split('_')
        signature = [0] * self._sig_len
        sig_buffer = [0] * self._sig_len
        quantity = 1.0
        quantity_buffer = 1.0
        in_numerator = True
        was_unit = False

        for token in tokens:
            if token == 'per':
                if not in_numerator:
                    raise ValueError("Multiple uses of keyword 'per' not allowed")
                in_numerator = False
                was_unit = False
            elif token == 'squared' or token == 'cubed':
                if not was_unit:
                    # Can't do 'per_squared' or 'cubed_squared' or even
                    # 'squared_meters'
                    raise ValueError(f'Invalid use of keyword {token}.')

                # Previous token was a unit, so squared and cubed are
                # valid modifiers. The modifiers are applied to the
                # contents of sig_buffer and quantity_buffer.
                if token == 'cubed':
                    for si in range(self._sig_len):
                        sig_buffer[si] *= 2

                    quantity_buffer *= quantity_buffer

                if in_numerator:
                    for si in range(self._sig_len):
                        signature[si] += sig_buffer[si]

                    quantity *= quantity_buffer
                else:
                    for si in range(self._sig_len):
                        signature[si] -= sig_buffer[si]

                    quantity /= quantity_buffer

                was_unit = False
            elif token in self._units:
                sig_buffer = list(self._units[token].signature)
                quantity_buffer = self._units[token].quantity

                if in_numerator:
                    for si in range(self._sig_len):
                        signature[si] += sig_buffer[si]

                    quantity *= quantity_buffer
                else:
                    for si in range(self._sig_len):
                        signature[si] -= sig_buffer[si]

                    quantity /= quantity_buffer

                was_unit = True
            else:
                raise ValueError(f'Unit not recognized: {token}')

        return _UnitSpec(signature=tuple(signature), quantity=quantity)

    def _parse_physical_quantity(self, physical_quantity: str) -> tuple[float, str]:
        """Parse physical quantity string.

        Parameters
        ----------
        physical_quantity : str
           String representing a physical quantity, like "5 feet".

        Returns
        -------
        quantity : float
           The quantity.
        units : str
           The units.

        """
        double_re = r'[-+]?[0-9]*\.?[0-9]+'
        fraction_re = r'[-+]?[0-9]+/[0-9]+'
        number_re = r'(?:' + fraction_re + r'|' + double_re + r')'
        composite_unit_re = r'[a-zA-Z_]+'
        physical_quantity_re_with_names = (
            r'(' + number_re + r')\s*(' + composite_unit_re + r')'
        )
        result = re.match(physical_quantity_re_with_names, physical_quantity)
        if result:
            quantity = float(Fraction(result.group(1)))
            units = result.group(2)
            return quantity, units
        else:
            raise ValueError('Invalid format')

    def _parse_unit_file(self, file: str | Path) -> None:
        """Parse Unit Definition File.

        Parameters
        ----------
        file : str | Path
            Location of unit definitions (see Syntax).

        Syntax
        ------
        The Unit Definition File consists of unit definitions and
        potentially comments. A comment starts with a # and can be on
        the same line as a unit specification, or on a line of its
        own. White space is ignored, but each unit specification must
        be on its own line.

        Units can either be specified by a vector representing its
        dimensional signature, or in terms of other units. Defining a
        unit by its dimensional signature looks like this:
           second: [1 0 0]
        This fairly meaninglessly defines a second as having that
        signature, with an implicit quantity of 1. Units defined in
        terms of their dimensional signatures can be used as a
        foundation to defined other units. For example, let's
        additionally define:
           meter: [0 1 0]
           kilogram: [0 0 1]
           newton: kilogram_meter_per_second_squared
        We have now seen our first unit definition in terms of other
        units. The syntax of unit specifications is described in the
        class documentation.

        """
        ## Regular expressions
        # This regular expression represents a line that contains nothing but
        # comments or spaces. Examples:
        # # This is a comment!
        #             # This is also a comment!
        empty_line_re = r'(^\s*(#.*)?$)'

        unit_re = r'[a-zA-Z]+'
        composite_unit_re = r'[a-zA-Z_]+'

        # This regular expression matches a double.
        # Source: http://www.regular-expressions.info/floatingpoint.html
        double_re = r'[-+]?[0-9]*\.?[0-9]+'
        fraction_re = r'[-+]?[0-9]+/[0-9]+'
        number_re = r'(?:' + fraction_re + r'|' + double_re + r')'

        # This regular expression represents a row vector, using Matlab
        # notation. Examples:
        # [1,1]
        # [ 1 , 1, 2.3 ]
        vector_re = r'\[\s*((\s*' + double_re + r'\s*,?)*\s*(' + double_re + r'))\s*\]'

        # This regular expression represents a physical quantity. Examples:
        #   1 day
        #   60 seconds
        #   1/3 tablespoons
        physical_quantity_re = number_re + r'\s*' + composite_unit_re
        physical_quantity_re_with_names = (
            r'(' + number_re + r')\s*(' + composite_unit_re + r')'
        )

        # This regular expression represents a unit specification.
        # Example:
        #  second: [0 0 1] # Irrelevant comment
        # Resulting tokens:
        #  token.key = 'second'
        #  token.value = '[0 0 1]'
        # Example:
        #  minute: 60 seconds # Irrelevant comment
        # Resulting tokens:
        #  token.key = 'minute'
        #  token.value = '60 seconds'
        key_value_re = (
            r'^\s*('
            + unit_re
            + r')\s*:\s*('
            + vector_re
            + r'|'
            + physical_quantity_re
            + r')\s*(#.*)?$'
        )

        ## Parse file
        with open(file) as f:
            line_number = 0
            for line in f:
                line_number += 1

                if re.match(empty_line_re, line):
                    # This line is a comment
                    continue

                result = re.match(key_value_re, line)

                if not result:
                    raise ValueError(f'Syntax error on line: {line_number}:')

                unit_name = result.group(1)
                definition = result.group(2)

                if unit_name in self._units:
                    raise ValueError(
                        f'Syntax error on line: {line_number}:'
                        f' Unit {unit_name} has already been specified.'
                    )

                if not re.match(r'^[a-zA-Z]+$', unit_name):
                    raise ValueError(
                        f'Syntax error on line: {line_number}:'
                        f' Unit names may contain only alphabetic characters'
                    )

                defined_by_signature = re.match(vector_re, definition)
                if defined_by_signature:
                    # Unit is specified by signature; in this case,
                    # quantity is by definition unity.
                    sig_strs = re.compile(r',|\s+,?\s*').split(
                        defined_by_signature.group(1)
                    )
                    sig = tuple(int(s) for s in sig_strs)

                    if self._sig_len == -1:
                        self._sig_len = len(sig)
                    elif len(sig) != self._sig_len:
                        raise ValueError(
                            f'Syntax error on line: {line_number}:'
                            f' Signature length inconsistent with previous units.'
                        )

                    self._units[unit_name] = _UnitSpec(signature=sig, quantity=1.0)
                else:
                    result = re.match(physical_quantity_re_with_names, definition)
                    if result:
                        this_quantity = float(Fraction(result.group(1)))
                        unit = result.group(2)

                        if this_quantity <= 0:
                            raise ValueError('Quantity must be strictly positive.')

                        sq = self._signature_and_quantity_for_unit(unit)
                        self._units[unit_name] = _UnitSpec(
                            signature=sq.signature,
                            quantity=sq.quantity * this_quantity,
                        )

    @overload
    def convert(self, physical_quantity: str, desired_units: str, /) -> float: ...
    @overload
    def convert(self, quantity: float, units: str, desired_units: str, /) -> float: ...
    def convert(
        self,
        a: str | float,
        b: str,
        c: str | None = None,
        /,
    ) -> float:
        """Convert from one unit to another.

        Two call shapes are accepted:

        - ``convert("5 feet", "meters")`` — parse the source quantity from a
          single string.
        - ``convert(5, "feet", "meters")`` — pass the numeric value and source
          unit separately.

        Returns
        -------
        float
            The input quantity expressed in ``desired_units``.

        Raises
        ------
        ValueError
            If the source and destination units have incompatible signatures,
            or if the two-argument form is called with a non-string source.

        """
        if c is None:
            if not isinstance(a, str):
                raise ValueError('Two-argument form requires a string like "5 feet"')
            quantity, units = self._parse_physical_quantity(a)
            desired_units = b
        else:
            quantity = float(a)
            units = b
            desired_units = c

        given_sq = self._signature_and_quantity_for_unit(units)
        given_sig = given_sq.signature
        given_quant = given_sq.quantity
        des_sq = self._signature_and_quantity_for_unit(desired_units)
        des_sig = des_sq.signature
        des_quant = des_sq.quantity

        for fi, ti in zip(given_sig, des_sig, strict=True):
            if fi != ti:
                raise ValueError('Units not compatible.')

        return quantity * given_quant / des_quant

    def add(self, x: str, y: str, sum_units: str) -> float:
        """Add physical quantities.

        Parameters
        ----------
        x : str
            String representing a physical quantity, like "5 meters".
        y : str
            String representing a physical quantity, like "2
            feet". Must have same signature as x.
        sum_units : str
            Desired units of sum, like "yards". Must have the same
            signature as both x and y.

        Returns
        -------
        quantity : float
            Number representing the sum of x and y in the specified
            units.

        Usage
        -----
        > from unit_parser import UnitParser
        > up = UnitParser()
        > x = "5 meters"
        > y = "2 feet"
        > up.add(x, y, "yards")
         6.13473315836

        """
        x_quant, x_units = self._parse_physical_quantity(x)
        y_quant, y_units = self._parse_physical_quantity(y)

        x_sq = self._signature_and_quantity_for_unit(x_units)
        y_sq = self._signature_and_quantity_for_unit(y_units)

        x_sig = x_sq.signature
        x_unit_quant = x_sq.quantity
        y_sig = y_sq.signature
        y_unit_quant = y_sq.quantity

        for i in range(self._sig_len):
            if x_sig[i] != y_sig[i]:
                raise ValueError('Units not compatible.')

        sum_quantity = x_quant * x_unit_quant + y_quant * y_unit_quant
        sum_signature = list(x_sig)

        sum_sq = self._signature_and_quantity_for_unit(sum_units)
        sum_sig = sum_sq.signature
        sum_unit_quant = sum_sq.quantity
        for i in range(self._sig_len):
            if sum_sig[i] != sum_signature[i]:
                raise ValueError('Units not compatible.')

        return sum_quantity / sum_unit_quant

    def subtract(self, x: str, y: str, diff_units: str) -> float:
        """Subtract physical quantities.

        Parameters
        ----------
        x : str
            String representing a physical quantity, like "5 meters".
        y : str
            String representing a physical quantity, like "2
            feet". Must have same signature as x.
        diff_units : str
            Desired units of difference, like "yards". Must have the
            same signature as both x and y.

        Returns
        -------
        quantity : float
            Number representing x minus y in the specified units.

        Usage
        -----
        > from unit_parser import UnitParser
        > up = UnitParser()
        > x = "5 meters"
        > y = "2 feet"
        > up.subtract(x, y, "yards")
         4.80139982502

        """
        x_quant, x_units = self._parse_physical_quantity(x)
        y_quant, y_units = self._parse_physical_quantity(y)

        x_sq = self._signature_and_quantity_for_unit(x_units)
        y_sq = self._signature_and_quantity_for_unit(y_units)

        x_sig = x_sq.signature
        x_unit_quant = x_sq.quantity
        y_sig = y_sq.signature
        y_unit_quant = y_sq.quantity

        for i in range(self._sig_len):
            if x_sig[i] != y_sig[i]:
                raise ValueError('Units not compatible.')

        diff_quantity = x_quant * x_unit_quant - y_quant * y_unit_quant
        diff_signature = list(x_sig)

        diff_sq = self._signature_and_quantity_for_unit(diff_units)
        diff_sig = diff_sq.signature
        diff_unit_quant = diff_sq.quantity
        for i in range(self._sig_len):
            if diff_sig[i] != diff_signature[i]:
                raise ValueError('Units not compatible.')

        return diff_quantity / diff_unit_quant

    def multiply(self, x: str, y: str, product_units: str) -> float:
        """Multiply physical quantities.

        Parameters
        ----------
        x : str
            String representing a physical quantity, like "5 meters_per_sec"
        y : str
            String representing a physical quantity, like "2 kg"
        product_units : str
            Desired units of product, like "kg_meters_per_sec". Must
            have the same signature as the product of x and y would
            have. Function will raise a ValueError if you try to
            multiply "meters_per_sec" and "kg" and express the product
            in "meters_per_sec_squared".

        Returns
        -------
        quantity : float
            Number representing the product of x and y in the
            specified units.

        Usage
        -----
        > from unit_parser import UnitParser
        > up = UnitParser()
        > x = "5 meters_per_second_squared"
        > y = "2 kg"
        > up.multiply(x, y, "newtons")
         10
        > up.multiply(x, y, "pounds")
         2.248089431

        """
        x_quant, x_units = self._parse_physical_quantity(x)
        y_quant, y_units = self._parse_physical_quantity(y)

        x_sq = self._signature_and_quantity_for_unit(x_units)
        y_sq = self._signature_and_quantity_for_unit(y_units)

        x_sig = x_sq.signature
        x_unit_quant = x_sq.quantity
        y_sig = y_sq.signature
        y_unit_quant = y_sq.quantity

        product_quantity = x_quant * x_unit_quant * y_quant * y_unit_quant
        product_signature = [x_sig[i] + y_sig[i] for i in range(self._sig_len)]

        prod_sq = self._signature_and_quantity_for_unit(product_units)
        prod_sig = prod_sq.signature
        prod_unit_quant = prod_sq.quantity
        for i in range(self._sig_len):
            if prod_sig[i] != product_signature[i]:
                raise ValueError('Units not compatible.')

        return product_quantity / prod_unit_quant

    def divide(self, numerator: str, denominator: str, quotient_units: str) -> float:
        """Divide physical quantities.

        Parameters
        ----------
        numerator : str
            String representing a physical quantity, like "5 meters"
        denominator : str
            String representing a physical quantity, like "2 sec"
        quotient_units : str
            Desired units of quotient, like "meters_per_sec". Must have
            the same signature as the quotient would have. Function
            will raise a ValueError if you try to divide "meters" by
            "sec" and express the result in "meters_per_sec_squared".

        Returns
        -------
        quantity : float
            Number representing the quotient in the specified units.

        Usage
        -----
        > from unit_parser import UnitParser
        > up = UnitParser()
        > x = "5 meters"
        > y = "2 sec"
        > up.divide(x, y, "meters_per_sec")
         2.5
        > up.divide(x, y, "feet_per_sec")
         8.20209973753

        """
        num_quant, num_units = self._parse_physical_quantity(numerator)
        denom_quant, denom_units = self._parse_physical_quantity(denominator)

        num_sq = self._signature_and_quantity_for_unit(num_units)
        denom_sq = self._signature_and_quantity_for_unit(denom_units)

        num_sig = num_sq.signature
        num_unit_quant = num_sq.quantity
        denom_sig = denom_sq.signature
        denom_unit_quant = denom_sq.quantity

        quotient_quantity = (num_quant * num_unit_quant) / (
            denom_quant * denom_unit_quant
        )
        quotient_signature = [num_sig[i] - denom_sig[i] for i in range(self._sig_len)]

        quot_sq = self._signature_and_quantity_for_unit(quotient_units)
        quot_sig = quot_sq.signature
        quot_quant = quot_sq.quantity
        for i in range(self._sig_len):
            if quot_sig[i] != quotient_signature[i]:
                raise ValueError('Units not compatible.')

        return quotient_quantity / quot_quant
