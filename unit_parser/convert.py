from __future__ import print_function
from unit_parser import unit_parser

#   File: convert.py
#   Purpose: Wrapper for command line utility for converting between
#   units.
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


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Unit conversions')
    parser.add_argument('quantity', type=float, help='Given quantity')
    parser.add_argument('given_units', type=str, help='Given units')
    parser.add_argument('desired_units', type=str, nargs='+', help='Desired units')

    args = parser.parse_args()
    quantity = args.quantity
    given_units = args.given_units
    if len(args.desired_units) == 1:
        desired_units = args.desired_units[0]
    else:
        desired_units = args.desired_units[1]
        
    up = unit_parser()
    desired_quantity = up.convert(quantity, given_units, desired_units)
    print(desired_quantity)

if __name__ == '__main__':
    main()
