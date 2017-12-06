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