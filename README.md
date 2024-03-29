# SimplePlanes to SimpleRockets 2 craft converter
![conversion result](images/craft.png)
Converts crafts from SimplePlanes to SimpleRockets 2. Many parts can't currently be converted (e.g. engines, see [Supported Parts](#supported-parts)) and some are converted poorly (see [Known Issues](#known-issues)), so some post-processing will be needed.
Was tested with Python 3.8.5, should work with Python 3.6+.

## Installation
On Windows you can simply download the executable (it's under "Releases" on the right side of the page) and run it. 

On other systems you will need to install Python 3 and do the following:
```console
$ git clone https://github.com/povle/SP-SR2-converter.git
$ cd SP-SR2-converter
$ python3 -m pip install -r requirements.txt
```

## Usage
You can either use the GUI (simply run `convert.py` without any arguments) or the CLI:
```console
$ python3 convert.py --help
usage: convert.py [-h] (--input_file INPUT_FILE | --id ID) [--output_file OUTPUT_FILE] [--scale SCALE] [--only_ids [part_id [part_id ...]] |
                  --exclude_ids [part_id [part_id ...]]] [--only_types [SP_type [SP_type ...]] | --exclude_types [SP_type [SP_type ...]]]

optional arguments:
  -h, --help            show this help message and exit

Basic Options:
  --input_file INPUT_FILE, -i INPUT_FILE
                        path to the source craft xml
  --id ID               ID of the craft (https://www.simpleplanes.com/a/??????/)
  --output_file OUTPUT_FILE, -o OUTPUT_FILE
                        path to the output file

Advanced Options:
  --scale SCALE, -s SCALE
                        scale of the converted craft
  --only_ids [part_id [part_id ...]]
                        convert only parts with given ids
  --exclude_ids [part_id [part_id ...]]
                        ignore parts with given ids
  --only_types [SP_type [SP_type ...]]
                        convert only parts with given types
  --exclude_types [SP_type [SP_type ...]]
                        ignore parts with given types
```
### Examples

```console
# convert https://www.simpleplanes.com/a/bAMO2A/Ilya-Muromets, save to bAMO2A_SR.xml
$ python3 convert.py --id bAMO2A

# convert the same craft but only fuselage blocks and fuselage cones
$ python3 convert.py --id bAMO2A --only_types Fuselage-Body-1 Fuselage-Cone-1

# convert the same craft but ignore parts with ids 3, 4, 5
$ python3 convert.py --id bAMO2A --exclude_ids 3 4 5

# convert crafts/ILUHA.xml, scale it by the factor of 2
$ python3 convert.py -i crafts/ILUHA.xml -s 2
```

## Supported Parts

 - Fuselage Block (`Fuselage-Body-1`)
 - Fuselage Cone (`Fuselage-Cone-1`)
 - Fuselage Inlet (`Fuselage-Inlet-1`)
 - Hollow Fuselage (`Fuselage-Hollow-1`)
 - Wings (`Wing-2`, `Wing-3`)
 - Blocks (`Block-1`, `Block-2`)
 - Actuators (`Piston`, `SmallRotator-1`, `HingeRotator-1`)

## Known Issues

 - Some parts (e.g. wings) have more attachment points in SP, crafts using those may not be able to load in SR2.
 - SR2 has a hard limit on the number of colors in a theme, SP does not.
 - In SR2 corners always scale with the part, in SP "Smooth" corners are constant radius.
 - Converted crafts often look darker for some reason.
 - Control surfaces occasionally get inverted.
 - Hollow fuselages are converted into regular ones.
 - Fuselage inlets can't be converted properly because they are a lot more customizable in SP.

If the converted craft does not load, you should try again with the dev console open and read the error messages. In some cases removing troublesome parts when converting (`--exclude-ids` option) can help.

## Acknowledgements
A huge thanks to [LegendaryBottle](https://www.simpleplanes.com/u/LegendaryBottle) for allowing to use his awesome [Ilya Muromets replica](https://www.simpleplanes.com/a/bAMO2A/Ilya-Muromets) as an example.
