# unit_parser: Unit Parser and Conversions

<table>
<tr>
  <td>Build Status</td>
  <td>
    <a href="https://travis-ci.org/rwilson4/unit_parser">
    <img src="https://travis-ci.org/rwilson4/unit_parser.svg?branch=master&label=Travis%20CI" alt="travis build status" />
    </a>
  </td>
</tr>
<tr>
  <td>Code Coverage</td>
  <td>
    <a href="https://codecov.io/gh/rwilson4/unit_parser">
    <img src="https://codecov.io/gh/rwilson4/unit_parser/branch/master/graph/badge.svg" />
    </a>
  </td>
</tr>
</table>

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

As mentioned above, this library ships with a unit specification
file. It contains many of the most common units, but you may find some
glaring omissions. For your particular use case, you may prefer to
create your own unit specification file and include that with your
application. The unit specification file syntax is simple, if not
intuitive. The file is plain-text, with key-value pairs separated by a
colon. Comments may be included and begin with a semi-colon. Units are
either specified as primitives, or in terms of other units. A
primitive definition consists of specifying the signature of the unit,
which is represented as a vector of non-negative integers. For example:
````sh
second: [1 0 0]
````
The entries of this vector correspond to the exponents of units in an
arbitrary order that nonetheless needs to be consistent throughout the
application. We might arbitrarily decide that time units go first,
then length, then mass. Then since force has dimension mass times
length divided by time squared, all units of force have signature [-2
1 1]. The way we define the second really just tells the program which
index (the first) corresponds to a particular primitive. A more
complete specification might look like this:
````sh
second: [1 0 0]
meter: [0 1 0]
kilogram: [0 0 1]
minute: 60 second
hour: 60 minute
# We can define a newton either like this:
newton: 1 kilogram_meter_per_second_squared
# or like this:
# newton: [-2 1 1]
# (first way preferred).
````
Once we have defined the "primitive" units, it is simple and intuitive
to define other units recursively in terms of previously specified
units. For example, the newton could have been defined in terms of its
signature, but it is better to define it in terms of kilograms,
meters, and seconds. A pound (of force) could *not* have been defined
in terms of its signature, because although it has the same signature,
it has a different quantity. Meaning, a pound is *not* equal to one
kilogram meter per second squared, and defining units in terms of
signatures implicitly assumes the quantity is one.

The included unit specification file uses MKS (meters, kilograms,
seconds) as the base, but as long as the internal specification is
consistent, that is transparent to the user of such a file. A unit
specification file using imperial units as the base would be just as
valid, and the end user would never even notice.

If you are the sort of person that enjoys reading esoteric Wikipedia
pages, the flexible syntax gives the fun opportunity to look up the
official definitions of units, and using that in the file. For
example, it turns out the slug, which is a unit of mass in the
imperial system, is actually defined as one pound of force times one
second squared per foot. So this unit of mass is actually defined in
terms of a unit of force, even though conceptually mass seems like the
more primitive notion! The included unit file tries to be faithful to
these definitions. The reader may quite reasonably ask if it makes any
difference. The answer is no, except perhaps for the fun of it. (If
you are *not* the sort of person who enjoys reading esoteric Wikipedia
articles, this whole paragraph makes me sound like a weirdo.)

Finally, this library ships with a command line utility called
"convert". This can be run from the command line like so:
````sh
$ convert 5 feet to meters
1.524
````
(The "to" is optional, but I find it more intuitive to include it.)
