"""Command-line entry point for unit conversion."""

import argparse

from .units import UnitParser


def main() -> float:
    parser = argparse.ArgumentParser(description='Unit conversions')
    parser.add_argument('quantity', type=float, help='Given quantity')
    parser.add_argument('given_units', type=str, help='Given units')
    parser.add_argument(
        'desired_units',
        type=str,
        nargs='+',
        help='Desired units, optionally preceded by the filler word "to"',
    )

    args = parser.parse_args()

    if len(args.desired_units) == 1:
        desired_units = args.desired_units[0]
    elif len(args.desired_units) == 2 and args.desired_units[0] == 'to':
        desired_units = args.desired_units[1]
    else:
        parser.error(
            'expected destination unit, optionally preceded by "to"; got: '
            f'{" ".join(args.desired_units)!r}'
        )

    up = UnitParser()
    desired_quantity = up.convert(args.quantity, args.given_units, desired_units)
    print(desired_quantity)
    return desired_quantity


if __name__ == '__main__':
    main()
