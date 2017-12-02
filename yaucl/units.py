#!/usr/bin/python

# SYNTAX
#   parseUnitFile(file)
# DESCRIPTION
#   This function reads a file defining the various units that may be used.
# INPUTS
#   file      File defining units. The file must have a specific format, as
#             described below.
# FILE FORMAT
#   The definition file consists of unit definitions, and possibly white
#   space and comments. Unit definitions are not allowed to span lines, but
#   are otherwise unaffected by whitespace. There are two types of
#   definitions: fundamental and derived. A fundamental definition merely
#   specifies the signature of the unit. The quantity is required to be
#   unity. For definitions and examples of signature and quantity, see the
#   comments in convertUnits.m.
#
#   Here is an example of a fundamental definition:
#      second  : [0 0 1]
#   The name of the unit comes first, then a semicolon, then a row vector
#   specifying the signature. The unit name is restricted to contain only
#   alphabetic characters (a through z), and is case insensitive. The row
#   vector uses standard Matlab notation, delimited by square brackets,
#   with entries separated by spaces. A single comma is permitted and
#   equivalent to a space. For example, [0, 0 1] is equivalent to the above
#   example, but [0,, 0 1] is invalid, just as it would be in Matlab.
#
#   Here is an example of a derived definition:
#      minute: 60 second
#   Derived units are multiples of previously defined units.
#
#   Certain combinations of units are automatically recognized, as
#   discussed in the comments in convertUnits.m. For example, consider the
#   following derived definition:
#      newton: 1 kilogram_meter_per_second_squared.
#   Provided kilogram, meter, and second had previously been defined, the
#   code automatically recognizes this sort of expression for what it is.
#   Note that 'per', 'squared', and 'cubed' are reserved keywords that
#   cannot be the names of units.

import re
import sys

class units:
    def __init__(self):
        self.units = {}
        self.sigLen = -1
    
    def signatureAndQuantityForUnit(self, unit):
        if unit in self.units:
            return self.units[unit]
        else:
            # Parse string
            tokens = unit.split('_')
            signature = [0] * self.sigLen
            thisSignature = [0] * self.sigLen
            quantity = 1
            thisQuantity = 1
            numFlag = True
            wasUnit = False

            for token in tokens:
                if token == 'per':
                    wasUnit = False
                    numFlag = False
                elif (token == 'squared' or token == 'cubed'):
                    if wasUnit:
                        # Previous token was a unit, so squared and cubed
                        # are valid modifiers. More importantly,
                        # thisSignature and thisQuantity are still
                        # applicable.
                        if token == 'cubed':
                            for si in (range(len(thisSignature))):
                                thisSignature[si] *= 2
                                
                            thisQuantity *= thisQuantity

                        if numFlag:
                            for si in (range(len(thisSignature))):
                                signature[si] += thisSignature[si]
                                
                            quantity *= thisQuantity
                        else:
                            for si in (range(len(thisSignature))):
                                signature[si] -= thisSignature[si]
                                
                            quantity /= thisQuantity

                        wasUnit = False
                    else:
                        print('Invalid use of keyword {0:s}.'.format(token))
                        sys.exit()
                elif token in self.units:
                    thisSignature = list(self.units[token]['signature'])
                    thisQuantity = self.units[token]['quantity']

                    if numFlag:
                        for si in (range(len(thisSignature))):
                            signature[si] += thisSignature[si]

                        quantity *= thisQuantity
                    else:
                        for si in (range(len(thisSignature))):
                            signature[si] -= thisSignature[si]

                        quantity /= thisQuantity

                    wasUnit = True
                else:
                    print('Unit not recognized: {0:s}'.format(token))
                    sys.exit()

            return {'signature': signature, 'quantity': quantity}

    def parseUnitFile(self, file):
        ## Regular expressions
        # This regular expression represents a line that contains nothing but
        # comments or spaces. Examples:
        # # This is a comment!
        #             # This is also a comment!
        emptyLineRE = '(^\s*(#.*)?$)'

        unitRE = '[a-zA-Z]+'
        compositeUnitRE = '[a-zA-Z_]+'

        # This regular expression matches a double.
        # Source: http://www.regular-expressions.info/floatingpoint.html
        doubleRE = '[-+]?[0-9]*\.?[0-9]+'

        # This regular expression represents a row vector, using Matlab notation.
        # Examples:
        # [1,1]
        # [ 1 , 1, 2.3 ]
        vectorRE = '\[\s*((\s*' + doubleRE + '\s*,?)*\s*(' + doubleRE + '))\s*\]'

        # This regular expression represents a physical quantity. Examples:
        #   1 day
        #   60 seconds
        physicalQuantityRE = doubleRE + '\s*' + compositeUnitRE
        physicalQuantityRENames = '(' + doubleRE + ')\s*(' + compositeUnitRE + ')'

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
        keyValueRE = '^\s*(' + unitRE + ')\s*:\s*(' + vectorRE + '|' + physicalQuantityRE + ')\s*(#.*)?$'

        ## Parse file
        with open(file, 'r') as f:
            lineNumber = 0
            for line in f:
                lineNumber += 1

                if re.match(emptyLineRE, line):
                    # This line is a comment
                    continue

                matchRes = re.match(keyValueRE, line)

                if not matchRes:
                    print('parseUnitFile:syntaxError')
                    sys.exit()

                unitName = matchRes.group(1)
                definition = matchRes.group(2)

                if unitName in self.units:
                    print('Unit {0:s} has already been specified.'.format(unitName))
                    sys.exit()

                if not re.match('^[a-zA-Z]+$', unitName):
                    print('Unit names may contain only alphabetic characters')
                    sys.exit()

                vecRes = re.match(vectorRE, definition)
                if vecRes:
                    # Unit is specified by signature; in this case,
                    # quantity is by definition unity.
                    sig = re.compile(',|\s+,?\s*').split(vecRes.group(1))
                    for isig in range(len(sig)):
                        sig[isig] = float(sig[isig])

                    sigLen = len(sig)
                    if (self.sigLen == -1):
                        self.sigLen = sigLen
                    else:
                        if (sigLen != self.sigLen):
                            print('Signature length inconsistent with previous units.')
                            sys.exit()

                    self.units[unitName] = {'signature': sig, 'quantity': 1}
                else:
                    parseRes = re.match(physicalQuantityRENames, definition)
                    if parseRes:
                        thisQuantity = float(parseRes.group(1))
                        unit = parseRes.group(2)

                        if (thisQuantity <= 0):
                            print('Quantity must be strictly positive.')
                            sys.exit()

                        saq = self.signatureAndQuantityForUnit(unit)
                        sig = list(saq['signature'])
                        quantity = thisQuantity * saq['quantity']
                        self.units[unitName] = {'signature': sig, 'quantity': quantity}


    def convertUnits(self, quantity, fU, tU):
        fsaq = self.signatureAndQuantityForUnit(fU)
        tsaq = self.signatureAndQuantityForUnit(tU)

        for (fi, ti) in zip(fsaq['signature'], tsaq['signature']):
            if fi != ti:
                print('Units not compatible.')
                sys.exit()

        return quantity * fsaq['quantity'] / tsaq['quantity']
