# data-inventory
This is a python application for generating data-inventory for shp and gdb files either recursively through a directory or via a csv column containing paths to files to inventory and gather metadata on.

## Requirements
This applet is tested with python v3.8. You must have arcpy installed on your machine for this applet to work properly.

## Using the app
cd into the directory of this repository and run python main.py.

## Defaults
- the default for csv input will be ./input/data_inventory.csv
- the default output will be ./output/data_inventory.csv
