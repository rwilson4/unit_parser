#!/usr/bin/env python

from __future__ import print_function
from unit_parser import unit_parser

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
    desired_quantity = up.convert(str(quantity) + " " + given_units, desired_units)
    print(desired_quantity)

if __name__ == '__main__':
    main()
