# tsvarana.py
#
# Basic usage:
#	tsvarana.py --data <4d_nifti> --output <basename>
# 
# Inputs:
#	--data			[string] A 4-dimensional NIFTI file, typically a BOLD timeseries
#	--output		[string] Basename for output files
#	--slicedir 		[string] Slice-encode direction; x,y,z (default = z)
#	--threshold 	[scalar] Variance threshold for binary regressor generation (default = 5) 
#	--scrub 		[string] 'volume' (default), 'slice', 'off'
#	--save_var 		[logical] Save variance analysis as CSV files (default = false)
#	--save_reg		[logical] Save binary regressors as CSV files (default = false)
#	--save_varimg 	[logical] Save variance image as NIFTI files (default = false)
#
# Changelog
# 06/03/2020	Written
# 09/03/2020	Fixed NIFTI file writing
#				Input parser now enforces data type
#				Input parser now has compulsory arguments
#				Variance image outputted for each scrubbing iteration
#				Added slice-based scrubbing
#				Replaced volume-to-volume variance with volume vs. median variance
#
# Ivan Alvarez
# University of California, Berkeley

# ========
# SETTINGS
# ========

# Libraries
import sys
import argparse
import numpy as np
import nibabel as nib
from scipy.signal import find_peaks

# ============
# PARSE INPUTS
# ============

# Print help message if no arguments are provided
if len(sys.argv) == 0:
	print('tsvarana.py --data <4d_nifti> --output <basename>')
	sys.exit()

# Set up parser
parser = argparse.ArgumentParser()
parser.add_argument('--data', help='<4d_nifti>', type=str, required=True)
parser.add_argument('--output', help='<basename>', type=str, required=True)
parser.add_argument('--slicedir', help='<x/y/z>', type=str)
parser.add_argument('--threshold', help='<scalar>', type=float)
parser.add_argument('--scrub', help='<volume/slice/off>', default='volume', type=str)
parser.add_argument('--save_var', help='Output variance .csv file(s)', action='store_true')
parser.add_argument('--save_reg', help='Output regressor .csv file(s)', action='store_true')
parser.add_argument('--save_varimg', help='Output variance NIFTI file(s)', action='store_true')

# Set defaults
parser.set_defaults(slicedir='z')
parser.set_defaults(threshold=5)
parser.set_defaults(scrub='volume')
parser.set_defaults(save_var=False)
parser.set_defaults(save_reg=False)
parser.set_defaults(save_varimg=False)

# Parse input arguments
args = parser.parse_args()

# ====
# MAIN
# ====

def main(args):
	'''main'''

	# Get slice index
	sliceidx = slicepointer(args.slicedir)

	# Load image data
	header = nib.load(args.data)
	imdata = header.get_fdata()

	# Number of volumes and slices in 4D file
	nvol = imdata.shape[3]
	nslice = imdata.shape[sliceidx]

	# Make a copy of the data for scrubbing
	imdata_scrub = imdata

	# Binary volume and slice nulling regressors
	volumereg = np.full((1, nvol), False, dtype=bool)[0]
	slicereg = np.full((nvol, nslice), False, dtype=bool)

	# Iteration counter
	counter = 0

	# Loop
	while True:

		# Update counter
		counter += 1

		# Calculate variance
		volumevar, slicevar, varimg = tsvarana_calc(imdata_scrub, sliceidx)

		# Binary list of bad regressors
		badvolume, badslice = tsvarana_regressor(volumevar, slicevar, args.threshold)

		# Add to binary nulling regressors
		volumereg = volumereg + badvolume
		slicereg = slicereg + badslice

		# Volume-based scrubbing
		if args.scrub.lower() == 'volume':
			imdata_scrub = tsvarana_scrub_volume(imdata_scrub, volumereg)

		# Slice-based scrubbing
		elif args.scrub.lower() == 'slice':
			imdata_scrub = tsvarana_scrub_slice(imdata_scrub, slicereg, sliceidx)

		# Save iteration files
		tsvarana_save(args, counter, volumevar, slicevar, varimg, header)

		# Break out conditions
		if sum(badvolume) == 0 or args.scrub.lower() == 'off':
			break

	# Save final outputs
	tsvarana_save_final(args, volumereg, slicereg, imdata_scrub, header)

# =============
# SLICE POINTER
# =============

def slicepointer(dim):
	''' Define slice dimension as index '''

	switcher = {
		'x' : 0,
		'y' : 1,
		'z' : 2
	}
	return switcher.get(dim, 'Not a valid slice dimension')

# ====================
# VARIANCE CALCULATION
# ====================

def tsvarana_calc(imdata, sliceidx):
	'''Variance calculation for volumes and slices'''

	# Dimensions along which to sum for slices
	# Inelegant, I am sure there is a cleaner way to write this
	if sliceidx == 0:
		flattendim = (1,2)
	elif sliceidx == 1:
		flattendim = (0,2)
	elif sliceidx == 2:
		flattendim = (0,1)

	# Mean voxel intensity for each volume, across entire timeseries
	meanpixel = np.mean(imdata, axis=(0,1,2,3))

	# Variance image
	varimg = np.var(imdata, axis=3)

	# Number of volumes and slices in 4D file
	nvol = imdata.shape[3]
	nslice = imdata.shape[sliceidx]

	# Median volume
	medianvol = np.median(imdata, axis=3)

	# Empty variable for slice-wise variance
	slicevar = np.empty((nvol, nslice))
	slicevar.fill(np.nan)

	# Loop volumes
	for vol in range(0, nvol):

		# 2 volume sample
		sample = np.stack((imdata[:, :, :, vol], medianvol), axis=3)

		# Voxelwise variance between volume and median volume
		vw = np.var(sample, axis=3)

		# Mean variance across voxels, for each slice
		slicevar[vol, :] = np.mean(vw, axis=flattendim)

	# Average across slices
	volumevar = np.mean(slicevar, axis=1)

	# Normalise by mean intensity
	volumevar = volumevar / meanpixel
	slicevar = slicevar / meanpixel

	# Send back
	return volumevar, slicevar, varimg;

# ==========
# REGRESSORS
# ==========

def tsvarana_regressor(volumevar, slicevar, threshold):
	'''Create binary regressors for volumes and slices'''

	# Find volumes that violate the threshold
	badvolume = volumevar > threshold

	# Find slices that violate the threshold
	badslice = slicevar > threshold

	# Send back
	return badvolume, badslice;

# ======================
# VOLUME-BASED SCRUBBING
# ======================

def tsvarana_scrub_volume(imdata, volumereg):
	'''Perform volume-based timeseries scrubbing'''

	# Make a copy of the data
	imdata_scrub = imdata

	# Zero pad the regressor
	reg = np.pad(volumereg, (1,1), 'constant', constant_values=(False))

	# Locate volumes to remove
	_ , properties = find_peaks(reg, width=1)
	peaks = properties['left_bases'].astype('int')
	widths = properties['widths'].astype('int')

	# The peak 'left base' is the first non-peak point, so we want to
	# shift it by one to the right to ensure it's the index for the 
	# first reject volume
	# ... however, we also padded the array with zeros, so we need to 
	# shift the peak indices back to the lefy by one step as well
	# In summary, we should shift by one to the right (+1) and by one
	# to the right (-1), which cancel out

	# Loop peaks
	for p in range(0, len(peaks)):

		# Bad volume window
		window = np.arange(peaks[p], peaks[p] + widths[p])

		# Volumes before and after window
		prev = window[0] - 1
		post = window[-1] + 1

		# Average volumes before and after window, while dealing
		# with window edges

		# If both left- and right-side edges are available, 
		# average them
		if prev >= 0 and post < len(volumereg):
			insert = np.mean(imdata[:, :, :, [prev, post]], axis=3)

		# If the left-side edge is at the start of the run, 
		# take the single volume after the peak
		elif prev < 0 and post <= len(volumereg):
			insert = imdata[:, :, :, post]

		# If the right-side edge is after the end of the run,
		# take the single volume before the peak
		elif prev >= 0 and post >= len(volumereg):
			insert = imdata[:, :, :, prev]

		# If both conditions are violated, it means we are excluding
		# the entire run, and something has gone horribly wrong			
		else:
			raise SystemExit('Error: entire timeseries being excluded during scrubbing.')

		# Plug window edge average into scrubbed data
		imdata_scrub[:, :, :, window] = insert[:, :, :, np.newaxis]

	# Send back
	return imdata_scrub;

# =====================
# SLICE-BASED SCRUBBING
# =====================

def tsvarana_scrub_slice(imdata, slicereg, sliceidx):
	'''Perform slice-based timeseries scrubbing'''

	# Make a copy of the data
	imdata_scrub = imdata

	# Loop slices
	for s in range(0, slicereg.shape[1]):

		# This slice regressor
		reg = slicereg[:, s]

		# Zero pad the regressor
		reg = np.pad(reg, (1,1), 'constant', constant_values=(False))

		# Locate volumes to remove
		_ , properties = find_peaks(reg, width=1)
		peaks = properties['left_bases'].astype('int')
		widths = properties['widths'].astype('int')

		# The peak 'left base' is the first non-peak point, so we want to
		# shift it by one to the right to ensure it's the index for the 
		# first reject volume
		# ... however, we also padded the array with zeros, so we need to 
		# shift the peak indices back to the lefy by one step as well
		# In summary, we should shift by one to the right (+1) and by one
		# to the right (-1), which cancel out

		# Loop peaks
		for p in range(0, len(peaks)):

			# Bad volume window
			window = np.arange(peaks[p], peaks[p] + widths[p])

			# Volumes before and after window
			prev = window[0] - 1
			post = window[-1] + 1

			# Average volumes before and after window, while dealing
			# with window edges

			# If both left- and right-side edges are available, 
			# average them
			if prev >= 0 and post <= slicereg.shape[0]:
				insert = np.mean(imdata[:, :, :, [prev, post]], axis=3)

			# If the left-side edge is at the start of the run, 
			# take the single volume after the peak
			elif prev < 0 and post <= slicereg.shape[0]:
				insert = imdata[:, :, :, post]

			# If the right-side edge is after the end of the run,
			# take the single volume before the peak
			elif prev >= 0 and post > slicereg.shape[0]:
				insert = imdata[:, :, :, prev]

			# If both conditions are violated, it means we are excluding
			# the entire run, and something has gone horribly wrong			
			else:
				raise SystemExit('Error: entire timeseries being excluded during scrubbing.')

			# Plug window edge average into scrubbed data, in the selected slice
			if sliceidx == 0:
				imdata_scrub[s, :, :, window] = insert[s, :, :, np.newaxis]
			elif sliceidx == 1:
				imdata_scrub[:, s, :, window] = insert[:, s, :, np.newaxis]
			elif sliceidx == 2:
				imdata_scrub[:, :, s, window] = insert[:, :, s, np.newaxis]

	# Send back
	return imdata_scrub;

# ================
# SAVING ITERATION
# ================

def tsvarana_save(args, counter, volumevar, slicevar, varimg, header):
	'''Save iteration outputs'''

	# Save variance analysis
	if args.save_var:

		# Write CSV to file
		np.savetxt(args.output + '_volumevar' + str(counter) + '.csv', volumevar, delimiter = ',')
		np.savetxt(args.output + '_slicevar' + str(counter) + '.csv', slicevar, delimiter = ',')

	# Save variance image
	if args.save_varimg:

		# Write NIFTI to file
		img = nib.Nifti1Image(varimg, header.affine)
		nib.save(img, args.output + '_varimg' + str(counter) + '.nii.gz')

# ============
# SAVING FINAL
# ============

def tsvarana_save_final(args, volumereg, slicereg, imdata_scrub, header):
	'''Save final outputs'''

	# Save binary regressors
	if args.save_reg:

		# Write CSV to file
		np.savetxt(args.output + '_volumereg.csv', volumereg, fmt='%5.0f', delimiter = ',')
		np.savetxt(args.output + '_slicereg.csv', slicereg, fmt='%5.0f', delimiter = ',')

	# Save scrubbed data
	if args.scrub.lower() != 'off':

		# Write NIFTI
		img = nib.Nifti1Image(imdata_scrub, header.affine)
		nib.save(img, args.output + '_scrub.nii.gz')

# ====
# CALL
# ====

# Call
main(args)

# Done
#