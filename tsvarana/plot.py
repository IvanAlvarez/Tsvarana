# plot.py
#
# tsvarana plotting functions.
#
# Ivan Alvarez
# University of California, Berkeley

# =========
# LIBRARIES
# =========

# Libraries
import numpy as np
from bokeh import plotting
from bokeh import layouts
from bokeh import models
from bokeh import palettes

# ===============
# PLOT_DIAGNOSTIC
# ===============


def plot_diagnostic(varana, show=False, outfile=None):
    '''
    Plot diagnostics

    Inputs
        varana       [object] As created by tsvarana.classes.varana
        show         [ bool ] Show the plot
        outfile      [string] If specified, save plot as HTML file
    Output
        grid         [object] Figure grid handle
    '''

    # Use plot iterator
    grid = plot_iterator(varana, 'variance')

    # Show
    if show:
        plotting.show(grid)

    # Save figure
    if outfile:
        plotting.output_file(outfile)
        plotting.save(grid)

    # Return
    return grid

# ==============
# PLOT_REGRESSOR
# ==============


def plot_regressor(varana, show=False, outfile=None):
    '''
    Plot regressors

    Inputs
        varana       [object] As created by tsvarana.classes.varana
        show         [ bool ] Show the plot
        outfile      [string] If specified, save plot as HTML file
    Output
        grid         [object] Figure grid handle
    '''

    # Use plot iterator
    grid = plot_iterator(varana, 'regressor')

    # Show
    if show:
        plotting.show(grid)

    # Save figure
    if outfile:
        plotting.output_file(outfile)
        plotting.save(grid)

    # Return
    return grid

# =============
# PLOT_ITERATOR
# =============


def plot_iterator(varana, data_type):
    '''
    Plonk plots one of the top of the other, one per scrub iteration

    Inputs
        varana       [object] As created by tsvarana.classes.varana
        data_type    [string] variance, regressor
    Output
        grid         [object] Figure grid handle
    '''

    # Select data
    if data_type == 'variance':
        data_list = varana.variance
    elif data_type == 'regressor':
        data_list = varana.regressor

    # Empty plot handle list
    handles = []

    # Loop iterations
    for counter, data in enumerate(data_list):

        # Select plot type
        if varana.spatial_unit == 'volume':

            # Plot 1D
            handle = plot_1d(
                data,
                varana.summary_axis,
                varana.time_axis
            )

        elif varana.spatial_unit == 'slice':

            # Plot 2D
            handle = plot_2d(
                data,
                varana.summary_axis,
                varana.time_axis
            )

        elif varana.spatial_unit == 'voxel':

            # Not plotting 3D, because that's silly
            raise TypeError(
                'Error: Voxelwise variance diagnostic plot is not defined.'
            )

        # Change title
        new_title = models.annotations.Title()
        new_title.text = data_type + ' - iteration ' + str(counter + 1)
        handle.title = new_title

        # Store handle
        handles.append(handle)

    # Arrange plots
    grid = layouts.gridplot(handles, ncols=1)

    # Return
    return grid


# ======
# PLOT_1D
# ======


def plot_1d(data, summary_axis, time_axis):
    '''
    Plot variance analysis along 1D

    Inputs
        data         [array]  Voxelwise data
                              Can be scalar (vw_variance) or binary (regressor)
        summary_axis [tuple]  One or more axes to summarise variance
        time_axis    [scalar] Axis along which time is encoded

    Outputs
        handle       [object] Figure handle
    '''

    # Safety check
    if data.ndim - 1 != len(summary_axis):
        raise TypeError(
            'Error: incorrect number of summary axes specified.'
        )

    # Timepoints
    x = np.arange(data.shape[time_axis]) + 1

    # Mean across summary axes
    y = np.mean(data, axis=summary_axis)

    # Create figure
    handle = plotting.figure(
        plot_width=800,
        plot_height=500,
        title='',
        x_axis_label='Time (TR)',
        y_axis_label='Mean normalized variance',
        tools='pan,box_zoom,reset',
    )

    # If the array is binary, plot as step
    # Otherwise, plot as line
    if np.array_equal(y, y.astype(bool)):
        handle.step(x, y, line_width=2)
    else:
        handle.line(x, y, line_width=2)

    # Tidy
    handle.title.align = 'center'
    handle.xaxis.axis_label_text_align = 'center'
    handle.yaxis.axis_label_text_align = 'center'
    handle.xaxis.axis_label_text_font_size = '10pt'
    handle.yaxis.axis_label_text_font_size = '10pt'
    handle.xaxis.axis_label_text_font_style = 'normal'
    handle.yaxis.axis_label_text_font_style = 'normal'

    # Return
    return handle

# =======
# PLOT_2D
# =======


def plot_2d(data, summary_axis, time_axis):
    '''
    Plot variance analysis along 2D

    Inputs
        data         [array]  Voxelwise data
                              Can be scalar (vw_variance) or binary (regressor)
        summary_axis [tuple]  One or more axes to summarise variance
        time_axis    [scalar] Axis along which time is encoded

    Outputs
        handle       [object] Figure handle
    '''

    # Safety check
    if data.ndim - 2 != len(summary_axis):
        raise TypeError(
            'Error: incorrect number of summary axes specified.'
        )

    # Mean variance across summary axes
    y = np.mean(data, axis=summary_axis, keepdims=True)

    # Make time the 0th axis, squeeze and transpose
    # y = (slice, time)
    y = np.moveaxis(y, time_axis, 0)
    y = y.squeeze()
    y = y.T

    # Force data into float type
    y = y.astype(float)

    # Create figure
    handle = plotting.figure(
        plot_width=800,
        plot_height=500,
        title='',
        x_axis_label='Time (TR)',
        y_axis_label='Slice',
        tools='pan,box_zoom,reset',
        tooltips=[('x', '$x'), ('y', '$y'), ('value', '@image')]
    )

    # If the array is binary, set colour mapper to b/w
    # If it's not binary, use a continuous palette
    if np.array_equal(y, y.astype(bool)):

        # Grayscale colormap
        color_mapper = models.LinearColorMapper(
            palette=palettes.grey(2)[::-1],
            low=0,
            high=1,
        )
    else:
        # Continuous colormap
        color_mapper = models.LinearColorMapper(
            palette=palettes.Viridis256,
            low=0,
            high=np.max(y),
        )

    # Add image
    handle.image(
        image=[y],
        x=0,
        y=0,
        dh=y.shape[0],
        dw=y.shape[1],
        color_mapper=color_mapper,
        level='image'
    )

    # Create colorbar
    colorbar = models.ColorBar(
        color_mapper=color_mapper,
        label_standoff=12,
        border_line_color=None,
        location=(0, 0),
        ticker=models.AdaptiveTicker(),
    )

    # Add colorbar
    handle.add_layout(colorbar, 'right')

    # Tidy
    handle.x_range.range_padding = 0
    handle.y_range.range_padding = 0
    handle.grid.grid_line_width = 0.5
    handle.title.align = 'center'
    handle.xaxis.axis_label_text_align = 'center'
    handle.yaxis.axis_label_text_align = 'center'
    handle.xaxis.axis_label_text_font_size = '10pt'
    handle.yaxis.axis_label_text_font_size = '10pt'
    handle.xaxis.axis_label_text_font_style = 'normal'
    handle.yaxis.axis_label_text_font_style = 'normal'

    # Return
    return handle

# Done
#
