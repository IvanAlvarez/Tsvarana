# __main__.py
#
# Basic usage
#   python -m tsvarana --data <nifti>
#
# Inputs
#    data           [string] A 4D NIFTI fila
#    spatial_unit   [string] Calculate mean variance along the specified
#                            spatial unit: 'voxel', 'slice' or 'volume'
#    slice_axis     [scalar] Axis long which the slice dimension is defined
#                            default for (x,y,z,t) data is slice_axis=2
#    time_axis      [scalar] Axis long which time is stored
#                            default for (x,y,z,t) data is time_axis=3
#    var_threshold  [scalar] Normalised variance threshold for scrubbing
#    one_shot       [ bool ] If True, perform a single iteration of scrubbing
#    output         [string] Basename for output files
#
# Ivan Alvarez
# University of California, Berkeley

# =========
# LIBRARIES
# =========

# Libraries
import sys
import argparse

# Project dependencies
import tsvarana

# ============
# PARSE INPUTS
# ============

# Print help message if no arguments are provided
if len(sys.argv) == 0:
    print('tsvarana.py --data <nifti>')
    sys.exit()

# Set up parser
parser = argparse.ArgumentParser()
parser.add_argument('--data', help='<nifti>', type=str, required=True)
parser.add_argument('--spatial_unit', help='<voxel,slice,volume>', type=str)
parser.add_argument('--slice_axis', help='<int>', type=int)
parser.add_argument('--time_axis', help='<int>', type=int)
parser.add_argument('--var_threshold', help='<scalar>', type=float)
parser.add_argument('--one_shot', action='store_true')
parser.add_argument('--output', help='<basename>', type=str)

# Set defaults
parser.set_defaults(spatial_unit='voxel')
parser.set_defaults(slice_axis=2)
parser.set_defaults(time_axis=3)
parser.set_defaults(var_threshold=5)
parser.set_defaults(one_shot=False)
parser.set_defaults(output='tsvarana')

# Parse input arguments
args = parser.parse_args()

# ====
# MAIN
# ====

# Execute default tsvarana routine
tsvarana.command.default_routine(args)

# Done
#
