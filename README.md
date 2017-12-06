# unit_parser
Unit Parser and Conversions

This library is primarily for parsing strings representing physical
quantities, like "5 feet" or "88 miles_per_hour". It can also be used
for converting between compatible units.

There is really only one "public" function: convert, which is really
used for parsing program inputs. For example, suppose there is an
input (e.g. from a JSON) representing how much volume of water is to
be used in a recipe. The user is free to specify the input in whatever
units are most convenient, e.g. "2 gallons". The code that is parsing
this input might call:
```sh
  > from unit_parser import unit_parser
  > up = unit_parser() # Initialization required
  > water_volume_liters = up.convert(water_volume, "liters")
```
In this way, no assumptions need to be made about units the input is
in. The code requires the water volume to be expressed in liters, but
it doesn't need to know or care how it was specified.

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


