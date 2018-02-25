import re
import os

#   File: units.py
#   Purpose: main component of unit parser and converter.
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


class unit_parser:
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
    def __init__(self, unit_definitions=None):
        self._units = {}
        self._sig_len = -1
        if unit_definitions is not None:
            self._parse_unit_file(unit_definitions)
        else:
            this_dir, this_filename = os.path.split(__file__)
            UNIT_PATH = os.path.join(this_dir, "units", "units.txt")
            self._parse_unit_file(UNIT_PATH)

    def _signature_and_quantity_for_unit(self, unit):
        """Parse physical quantity.

        Parameters
        ----------
        unit : str
            String representing a physical quanitity, like
            "9.81 meters_per_second_squared"

        Returns
        -------
        signature : array_like
            The signature of the unit (a vector with non-negative
            integer values).
        quantity : float
            The quantity associated with the unit.

        """

        if unit in self._units:
            return {'signature': list(self._units[unit]['signature']),
                    'quantity': self._units[unit]['quantity']}

        # Parse string
        tokens = unit.split('_')
        signature = [0] * self._sig_len
        sig_buffer = [0] * self._sig_len
        quantity = 1
        quantity_buffer = 1
        in_numerator = True
        was_unit = False

        for token in tokens:
            if token == 'per':
                if not in_numerator:
                    raise SyntaxError("Multiple uses of keyword 'per' not allowed")
                in_numerator = False
                was_unit = False
            elif (token == 'squared' or token == 'cubed'):
                if not was_unit:
                    # Can't do 'per_squared' or 'cubed_squared' or even 'squared_meters'
                    raise SyntaxError('Invalid use of keyword {0:s}.'.format(token))

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
                sig_buffer = list(self._units[token]['signature'])
                quantity_buffer = self._units[token]['quantity']

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
                raise SyntaxError('Unit not recognized: {0:s}'.format(token))

        return {'signature': signature,
                'quantity': quantity}


    def _parse_physical_quantity(self, physical_quantity):
        """Parse physical quantity.

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
        double_re = '[-+]?[0-9]*\.?[0-9]+'
        composite_unit_re = '[a-zA-Z_]+'
        physical_quantity_re_with_names = '(' + double_re + ')\s*(' + composite_unit_re + ')'
        result = re.match(physical_quantity_re_with_names, physical_quantity)
        if result:
            quantity = float(result.group(1))
            units = result.group(2)
            return quantity, units
        else:
            raise SyntaxError('Invalid format')


    def _parse_unit_file(self, file):
        """Parse Unit Definition File

        Parameters
        ----------
        file : str
            Location of unit definitions (see Syntax).

        Returns
        -------
        (nothing)

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
        empty_line_re = '(^\s*(#.*)?$)'

        unit_re = '[a-zA-Z]+'
        composite_unit_re = '[a-zA-Z_]+'

        # This regular expression matches a double.
        # Source: http://www.regular-expressions.info/floatingpoint.html
        double_re = '[-+]?[0-9]*\.?[0-9]+'

        # This regular expression represents a row vector, using Matlab notation.
        # Examples:
        # [1,1]
        # [ 1 , 1, 2.3 ]
        vector_re = '\[\s*((\s*' + double_re + '\s*,?)*\s*(' + double_re + '))\s*\]'

        # This regular expression represents a physical quantity. Examples:
        #   1 day
        #   60 seconds
        physical_quantity_re = double_re + '\s*' + composite_unit_re
        physical_quantity_re_with_names = '(' + double_re + ')\s*(' + composite_unit_re + ')'

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
        key_value_re = '^\s*(' + unit_re + ')\s*:\s*(' + vector_re + '|' + physical_quantity_re + ')\s*(#.*)?$'

        ## Parse file
        with open(file, 'r') as f:
            line_number = 0
            for line in f:
                line_number += 1

                if re.match(empty_line_re, line):
                    # This line is a comment
                    continue

                result = re.match(key_value_re, line)

                if not result:
                    msg = 'Syntax error on line: {0:d}:'
                    raise SyntaxError(msg.format(line_number))

                unit_name = result.group(1)
                definition = result.group(2)

                if unit_name in self._units:
                    msg = 'Syntax error on line: {0:d}:'
                    msg += ' Unit {1:s} has already been specified.'
                    raise SyntaxError(msg.format(line_number, unit_name))

                if not re.match('^[a-zA-Z]+$', unit_name):
                    msg = 'Syntax error on line: {0:d}:'
                    msg += ' Unit names may contain only alphabetic characters'
                    raise SyntaxError(msg.format(line_number))

                defined_by_signature = re.match(vector_re, definition)
                if defined_by_signature:
                    # Unit is specified by signature; in this case,
                    # quantity is by definition unity.
                    sig = re.compile(',|\s+,?\s*').split(defined_by_signature.group(1))
                    for isig in range(len(sig)):
                        sig[isig] = int(sig[isig])

                    sig_len = len(sig)
                    if (self._sig_len == -1):
                        self._sig_len = sig_len
                    elif sig_len != self._sig_len:
                        msg = 'Syntax error on line: {0:d}:'
                        msg += ' Signature length inconsistent with previous units.'
                        raise SyntaxError(msg.format(line_number))

                    self._units[unit_name] = {'signature': sig, 'quantity': 1}
                else:
                    result = re.match(physical_quantity_re_with_names, definition)
                    if result:
                        this_quantity = float(result.group(1))
                        unit = result.group(2)

                        if (this_quantity <= 0):
                            raise SyntaxError('Quantity must be strictly positive.')

                        sq = self._signature_and_quantity_for_unit(unit)
                        sig = sq['signature']
                        quantity = sq['quantity']
                        self._units[unit_name] = {'signature': sig,
                                                  'quantity': (quantity * this_quantity)}


    def convert(self, *args):
        """Convert from one unit to another.

        This function can be used in two ways; see Usage.

        Parameters
        ----------
        physical_quantity : str
           String representing a physical quantity, like "5 feet"
        desired_units : str
           String corresponding to a unit specification, like "meters",
           representing the desired units.
        quantity : numeric
           Used in conjunction with 'units'
        units : string
           String corresponding to a unit specification, used in
           conjunction with 'quantity'.

        Returns
        -------
        quantity : numeric
           The input quantity converted to the desired units.

        Usage
        -----
        des_quantity = convert(physical_quantity, desired_units)
        des_quantity = convert(quantity, units, desired_units)

        To convert 5 feet into meters, do either of the following:
         > convert('5 feet', 'meters')
         > convert(5, 'feet', 'meters')

        """

        if len(args) == 2:
            physical_quantity = args[0]
            desired_units = args[1]
            quantity, units = self._parse_physical_quantity(physical_quantity)
        elif len(args) == 3:
            quantity = args[0]
            units = args[1]
            desired_units = args[2]
        else:
            msg = 'Function must be called with 2 or 3 arguments;'
            msg += ' see documentation'
            raise SyntaxError(msg)

        given_sq = self._signature_and_quantity_for_unit(units)
        given_sig = given_sq['signature']
        given_quant = given_sq['quantity']
        des_sq = self._signature_and_quantity_for_unit(desired_units)
        des_sig = des_sq['signature']
        des_quant = des_sq['quantity']

        for (fi, ti) in zip(given_sig, des_sig):
            if fi != ti:
                raise ValueError('Units not compatible.')

        return quantity * given_quant / des_quant


    def add(self, x, y, sum_units):
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
        > from unit_parser import unit_parser
        > up = unit_parser()
        > x = "5 meters"
        > y = "2 feet"
        > up.add(x, y, "yards")
         6.13473315836

        """
        x_quant, x_units = self._parse_physical_quantity(x)
        y_quant, y_units = self._parse_physical_quantity(y)

        x_sig_quant = self._signature_and_quantity_for_unit(x_units)
        y_sig_quant = self._signature_and_quantity_for_unit(y_units)

        x_sig = x_sig_quant['signature']
        x_unit_quant = x_sig_quant['quantity']
        y_sig = y_sig_quant['signature']
        y_unit_quant = y_sig_quant['quantity']

        for i in range(self._sig_len):
            if x_sig[i] != y_sig[i]:
                raise ValueError('Units not compatible.')

        sum_quantity = x_quant * x_unit_quant + y_quant * y_unit_quant
        sum_signature = [0] * self._sig_len
        for i in range(self._sig_len):
            sum_signature[i] = x_sig[i]

        sum_sig_quant = self._signature_and_quantity_for_unit(sum_units)
        sum_sig = sum_sig_quant['signature']
        sum_unit_quant = sum_sig_quant['quantity']
        for i in range(self._sig_len):
            if sum_sig[i] != sum_signature[i]:
                raise ValueError('Units not compatible.')

        return sum_quantity / sum_unit_quant


    def subtract(self, x, y, diff_units):
        """Add physical quantities.

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
        > from unit_parser import unit_parser
        > up = unit_parser()
        > x = "5 meters"
        > y = "2 feet"
        > up.subtract(x, y, "yards")
         4.80139982502

        """
        x_quant, x_units = self._parse_physical_quantity(x)
        y_quant, y_units = self._parse_physical_quantity(y)

        x_sig_quant = self._signature_and_quantity_for_unit(x_units)
        y_sig_quant = self._signature_and_quantity_for_unit(y_units)

        x_sig = x_sig_quant['signature']
        x_unit_quant = x_sig_quant['quantity']
        y_sig = y_sig_quant['signature']
        y_unit_quant = y_sig_quant['quantity']

        for i in range(self._sig_len):
            if x_sig[i] != y_sig[i]:
                raise ValueError('Units not compatible.')

        diff_quantity = x_quant * x_unit_quant - y_quant * y_unit_quant
        diff_signature = [0] * self._sig_len
        for i in range(self._sig_len):
            diff_signature[i] = x_sig[i]

        diff_sig_quant = self._signature_and_quantity_for_unit(diff_units)
        diff_sig = diff_sig_quant['signature']
        diff_unit_quant = diff_sig_quant['quantity']
        for i in range(self._sig_len):
            if diff_sig[i] != diff_signature[i]:
                raise ValueError('Units not compatible.')

        return diff_quantity / diff_unit_quant


    def multiply(self, x, y, product_units):
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
        > from unit_parser import unit_parser
        > up = unit_parser()
        > x = "5 meters_per_second_squared"
        > y = "2 kg"
        > up.multiply(x, y, "newtons")
         10
        > up.multiply(x, y, "pounds")
         2.248089431

        """
        x_quant, x_units = self._parse_physical_quantity(x)
        y_quant, y_units = self._parse_physical_quantity(y)

        x_sig_quant = self._signature_and_quantity_for_unit(x_units)
        y_sig_quant = self._signature_and_quantity_for_unit(y_units)

        x_sig = x_sig_quant['signature']
        x_unit_quant = x_sig_quant['quantity']
        y_sig = y_sig_quant['signature']
        y_unit_quant = y_sig_quant['quantity']

        product_quantity = x_quant * x_unit_quant * y_quant * y_unit_quant
        product_signature = [0] * self._sig_len
        for i in range(self._sig_len):
            product_signature[i] = x_sig[i] + y_sig[i]

        prod_sig_quant = self._signature_and_quantity_for_unit(product_units)
        prod_sig = prod_sig_quant['signature']
        prod_unit_quant = prod_sig_quant['quantity']
        for i in range(self._sig_len):
            if prod_sig[i] != product_signature[i]:
                raise ValueError('Units not compatible.')

        return product_quantity / prod_unit_quant


    def divide(self, numerator, denominator, quotient_units):
        """Divide physical quantities.

        Parameters
        ----------
        numerator : str
            String representing a physical quantity, like "5 meters"
        denominator : str
            String representing a physical quantity, like "2 sec"
        quotient_units : str
            Desired units of product, like "meters_per_sec". Must have
            the same signature as the quotient would have. Function
            will raise a ValueError if you try to divide "meters" by
            "sec" and express the product in "meters_per_sec_squared".

        Returns
        -------
        quantity : float
            Number representing the quotient in the specified units.

        Usage
        -----
        > from unit_parser import unit_parser
        > up = unit_parser()
        > x = "5 meters"
        > y = "2 sec"
        > up.divide(x, y, "meters_per_sec")
         2.5
        > up.divide(x, y, "feet_per_sec")
         8.20209973753

        """
        num_quant, num_units = self._parse_physical_quantity(numerator)
        denom_quant, denom_units = self._parse_physical_quantity(denominator)

        num_sig_quant = self._signature_and_quantity_for_unit(num_units)
        denom_sig_quant = self._signature_and_quantity_for_unit(denom_units)

        num_sig = num_sig_quant['signature']
        num_unit_quant = num_sig_quant['quantity']
        denom_sig = denom_sig_quant['signature']
        denom_unit_quant = denom_sig_quant['quantity']

        quotient_quantity = (num_quant * num_unit_quant) / (denom_quant * denom_unit_quant)
        quotient_signature = [0] * self._sig_len
        for i in range(self._sig_len):
            quotient_signature[i] = num_sig[i] - denom_sig[i]

        quot_sig_quant = self._signature_and_quantity_for_unit(quotient_units)
        quot_sig = quot_sig_quant['signature']
        quot_quant = quot_sig_quant['quantity']
        for i in range(self._sig_len):
            if quot_sig[i] != quotient_signature[i]:
                raise ValueError('Units not compatible.')

        return quotient_quantity / quot_quant
