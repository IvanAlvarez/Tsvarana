# utils.py
#
# tsvarana utility functions.
#
# Ivan Alvarez
# University of California, Berkeley

# =========
# LIBRARIES
# =========

# Libraries
import numpy as np

# =========
# UTILITIES
# =========


def parse_spatial_unit(spatial_unit, data_ndim, slice_axis, time_axis):
    '''
    Parse spatial unit to define summary axes, i.e. the axes
    along which variance will be averaged

    Input
        spatial_unit       [string] voxel, slice, volume
        data_ndim          [scalar] number of data axes
        slice_dir          [scalar] axis along which slices are defined
        time_axis          [scalar] axis along which time is stores
    Output
        summary_axis       [tuple ] axis indices
    '''

    # Options
    if spatial_unit == 'voxel':
        # Keep all spatial points
        summary_axis = []

    elif spatial_unit == 'slice':
        # Keep all axes that are not the time axis, nor the slice axis
        summary_axis = np.logical_and(
            np.arange(data_ndim) != slice_axis,
            np.arange(data_ndim) != time_axis,
        )

    elif spatial_unit == 'volume':
        # Keep all axes that are not the time axis
        summary_axis = np.arange(data_ndim) != time_axis

    # Turn to tuple indices
    summary_axis = tuple(np.where(summary_axis)[0])

    # Return
    return summary_axis


def regressor_final(reg_iter):
    '''
    Binary mask of all timepoints scrubbed

    Input
        reg_iter    [list] N-dimensional binary regressors
    Output
        regressor   [array] Logical sum of reg_iter
    '''

    # Stack along first axis
    regressor = np.stack(reg_iter, axis=0)

    # Logical sum across iterations
    regressor = np.sum(regressor.astype(bool), axis=0)

    # Return
    return regressor

# Done
#
