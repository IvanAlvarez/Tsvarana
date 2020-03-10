# tsvarana_plot.py
#
# Basic usage:
#	tsvarana_plot.py --input <basename> --output <basename>
# 
# Inputs:
#	--input		[string] Basename for tsvarana outputs 
#	--output 	[string] Basename for plot files created
#
# Changelog
# 10/03/2020	Written
#
# Ivan Alvarez
# University of California, Berkeley

# ========
# SETTINGS
# ========

# Libraries
import sys
import argparse
import glob
import numpy as np
import pandas as pd
from bokeh import plotting
from bokeh import layouts
from bokeh import models

# ============
# PARSE INPUTS
# ============

# Print help message if no arguments are provided
if len(sys.argv) == 0:
	print('tsvarana_plot.py --input <basename> --output <basename>')
	sys.exit()

# Set up parser
parser = argparse.ArgumentParser()
parser.add_argument('--input', help='<basename>', type=str, required=True)
parser.add_argument('--output', help='<basename>', type=str, required=True)

# Parse input arguments
args = parser.parse_args()

# ====
# MAIN
# ====

def main(args):
	'''main'''

	# Load tsvarana analysis results
	volumevar, slicevar, volumereg, slicereg = tsvarana_plot_load(args)

	# Infer properties
	niter = len(volumevar)

	# Empty plot handles
	plothandle = []

	# Loop iterations
	for i in range(0, niter):

		# Create volume variance plot
		pvol = tsvarana_plot_vol(volumevar[i], i + 1)

		# Create slice variance plot
		pslice = tsvarana_plot_slice(slicevar[i], i + 1)

		# Store handles
		plothandle.append(pvol)
		plothandle.append(pslice)

	# Plot final regressors
	pvolreg = tsvarana_plot_volreg(volumereg)
	pslicereg = tsvarana_plot_slicereg(slicereg)

	# Store handles
	plothandle.append(pvolreg)
	plothandle.append(pslicereg)

	# Arrange plots
	grid = layouts.gridplot(plothandle, ncols=2)

	# Save figure
	plotting.output_file(args.output + '.html')
	plotting.save(grid)

# ====
# LOAD
# ====

def tsvarana_plot_load(args):
	'''Load tsvarana results'''

	# Empty variables
	volumevar = []
	slicevar = []
	volumereg = []
	slicereg = []

	# load volume variance
	for file in glob.glob(args.input + '_volumevar*.csv'):
		volumevar.append(pd.read_csv(file))

	# load slice variance
	for file in glob.glob(args.input + '_slicevar*.csv'):
		slicevar.append(pd.read_csv(file))

	# load volume and regressors
	volumereg = pd.read_csv(args.input + '_volumereg.csv')
	slicereg = pd.read_csv(args.input + '_slicereg.csv')

	# Return
	return volumevar, slicevar, volumereg, slicereg;

# ====================
# PLOT VOLUME VARIANCE
# ====================

def tsvarana_plot_vol(volumevar, iteration):
	'''Plot volume variance'''

	# Create figure
	p = plotting.figure(
		title='Volume variance - iteration ' + str(iteration),
		x_axis_label='Volume (TR)',
		y_axis_label='Normalized variance',
		tools = "pan,box_zoom,reset"
		)

	# Infer properties
	nvol = volumevar.shape[0]

	# Pull data
	x = np.arange(nvol) + 1
	y = volumevar.to_numpy()[:,0]

	# Add line
	p.line(x, y, line_width = 2)

	# Tidy
	p.title.align = 'center'
	p.xaxis.axis_label_text_align = 'center'
	p.yaxis.axis_label_text_align = 'center'
	p.xaxis.axis_label_text_font_size = '10pt'
	p.yaxis.axis_label_text_font_size = '10pt'
	p.xaxis.axis_label_text_font_style = 'normal'
	p.yaxis.axis_label_text_font_style = 'normal'

	# Return handle
	return p;

# ===================
# PLOT SLICE VARIANCE
# ===================

def tsvarana_plot_slice(slicevar, iteration):
	'''Plot slice variance'''

	# Create figure
	p = plotting.figure(
		title='Slice variance - iteration ' + str(iteration),
		x_axis_label='Volume (TR)',
		y_axis_label='Slice',
		tools = "pan,box_zoom,reset",
		tooltips=[('x', '$x'), ('y', '$y'), ('value', '@image')]
		)

	# Infer properties
	nvol = slicevar.shape[0]
	nslice = slicevar.shape[1]

	# Pull data
	z = slicevar.to_numpy()
	z = np.transpose(z)

	# Add image
	p.image(image=[z], x=1, y=1, dw=nvol, dh=nslice, palette='Spectral11', level='image')

	# Add colorbar
	colormapper = models.LinearColorMapper(palette='Spectral11', low=1, high=np.max(z))
	colorbar = models.ColorBar(color_mapper=colormapper, label_standoff=12, location=(0,0))
	p.add_layout(colorbar, 'right')

	# Tidy
	p.x_range.range_padding = 0
	p.y_range.range_padding = 0
	p.grid.grid_line_width = 0.5
	p.title.align = 'center'
	p.xaxis.axis_label_text_align = 'center'
	p.yaxis.axis_label_text_align = 'center'
	p.xaxis.axis_label_text_font_size = '10pt'
	p.yaxis.axis_label_text_font_size = '10pt'
	p.xaxis.axis_label_text_font_style = 'normal'
	p.yaxis.axis_label_text_font_style = 'normal'

	# Return handle
	return p;

# ======================
# PLOT VOLUME REGRESSORS
# ======================

def tsvarana_plot_volreg(volumereg):
	'''Plot volume variance'''

	# Create figure
	p = plotting.figure(
		title='Volume variance regressor',
		x_axis_label='Volume (TR)',
		y_axis_label='',
		tools = "pan,box_zoom,reset"
		)

	# Infer properties
	nvol = volumereg.shape[0]

	# Pull data
	x = np.arange(nvol) + 1
	y = volumereg.to_numpy()[:,0]

	# Add line
	p.step(x, y, line_width = 2)

	# Tidy
	p.title.align = 'center'
	p.xaxis.axis_label_text_align = 'center'
	p.xaxis.axis_label_text_font_size = '10pt'
	p.xaxis.axis_label_text_font_style = 'normal'

	# Return handle
	return p;

# =====================
# PLOT SLICE REGRESSORS
# =====================

def tsvarana_plot_slicereg(slicereg):
	'''Plot slice variance'''

	# Create figure
	p = plotting.figure(
		title='Slice variance regressor',
		x_axis_label='Volume (TR)',
		y_axis_label='Slice',
		tools = "pan,box_zoom,reset",
		tooltips=[('x', '$x'), ('y', '$y'), ('value', '@image')]
		)

	# Infer properties
	nvol = slicereg.shape[0]
	nslice = slicereg.shape[1]

	# Pull data
	z = slicereg.to_numpy()
	z = np.transpose(z)

	# Add image
	p.image(image=[z], x=1, y=1, dw=nvol, dh=nslice, palette=('#000000', '#ffffff'), level='image')

	# Tidy
	p.x_range.range_padding = 0
	p.y_range.range_padding = 0
	p.grid.grid_line_width = 0.5
	p.title.align = 'center'
	p.xaxis.axis_label_text_align = 'center'
	p.yaxis.axis_label_text_align = 'center'
	p.xaxis.axis_label_text_font_size = '10pt'
	p.yaxis.axis_label_text_font_size = '10pt'
	p.xaxis.axis_label_text_font_style = 'normal'
	p.yaxis.axis_label_text_font_style = 'normal'

	# Return handle
	return p;

# ====
# CALL
# ====

# Call
main(args)

# Done
#