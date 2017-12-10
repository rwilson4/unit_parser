# unit_parser
Unit Parser and Conversions

This library is primarily for parsing strings representing physical
quantities, like "5 feet" or "88 miles_per_hour". It can also be used
for converting between compatible units and doing basic arithmetic
operations.

The parsing function does double duty as a method for converting
between units and is thus called "convert".
```sh
  > from unit_parser import unit_parser
  > up = unit_parser()
  > up.convert("3 gallons", "liters")
    11.356235352
```
Note the unit parser must be initialized before being used by calling
the unit_parser() function without any arguments. That uses the
built-in unit specification file to define the units recognized by
this library. If a unit is not supported, you can create your own unit
specification file and provide the file name to this function.

The next thing we see is that physical quantities and units are
represented by strings. I find this to be the most intuitive way of
interacting with physical quantities. (Aside, something like "3
gallons" is a physical quantity, while "liters" is a unit.)

Since we represent physical quantities by strings, it is trivial to
use the convert function to parse an input in unknown units, but
ensure it is in the appropriate units for the needs of the program.
For example, suppose we have a program that does calculations on
volumes of water. Suppose there is an input (e.g. from a JSON file)
representing how much volume of water is to be used. The user is free
to specify the input in whatever units are most convenient, e.g. "2
gallons". The code that is parsing this input might call:

```sh
  > import json
  > from unit_parser import unit_parser
  > up = unit_parser()
  > config = json.load(open('example.json', 'r'))
  > water_volume = config['water_volume']
  > water_volume_liters = up.convert(water_volume, "liters")
```

In this way, no assumptions need to be made about what units the input
is in. The code requires the water volume to be expressed in liters,
but it doesn't need to know or care how it was specified.

Although the above example seems trivial, perhaps the most interesting
feature is the flexible unit specification parsing. Units may be
specified by a definition file (built-in, or provide your own!), or by
combinations of units defined in that file.

For example, if 'second', 'meter', and 'kilogram' are defined by the
file, the specification 'kilogram_meter_per_second_squared' is valid
and parsed as expected. These compound specifications consist of
tokens separated by underscores. Tokens include previously defined
units like 'kilogram' as well as the special keywords 'per',
'squared', and 'cubed'.

The keyword 'per' may be used at most once per specification and
directs that all subsequent tokens belong in the denominator of the
unit.

The keywords 'squared' and 'cubed' indicate that the preceding token
should be repeated once or twice more, respectively. They cannot be
daisy chained, for example: 'meters_squared_squared' is not permitted,
but 'meters_squared_meters_squared' or 'meters_cubed_meters' would
be. They also only apply to the preceding token, so
'second_second_meter_meter' is equivalent to
'second_squared_meter_squared' but not 'second_meter_squared'.

Finally, 'second', 'seconds', and 'sec' are not automatically
treated as equivalent units, but the unit definition file can and
does create these as if they were aliases. For example, 'seconds'
is defined as '1 second'.

We also permit simple arithmetic operations on units. There are
functions "add", "subtract", "multiply", and "divide". Each function
takes three arguments: two physical quantities, and the desired units
of the answer.

```sh
  > from unit_parser import unit_parser
  > up = unit_parser()
  > up.add("5 meters", "2 feet", "yards")
    6.13473315836
  > up.subtract("5 meters", "2 feet", "yards")
    4.80139982502
  > up.multiply("5 meters_per_sec_squared", "2 kg", "pounds")
    2.248089431
  > up.divide("5 meters", "2 sec", "mph")
    5.59234073014
```
