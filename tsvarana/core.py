# core.py
#
# tsvarana core functions.
#
# Ivan Alvarez
# University of California, Berkeley

# =========
# LIBRARIES
# =========

# Libraries
import numpy as np
from scipy.signal import find_peaks

# =============
# VARIANCE_CALC
# =============


def variance_calc(data, time_axis):
    '''
    Calculate timeseries variance against median timepoint.

    Inputs
        data        [array ] N-dimensional voxelwise data array
        time_axis   [scalar] Axis along which time is encoded
                             e.g. for (x,y,z,t) data, time_axis=3

    Outputs
        vw_variance [array ] Voxelwise variance-to-mean array
    '''

    # Move the time axis to the front
    data = np.moveaxis(data, time_axis, 0)

    # Median timepoint
    median_img = np.median(data, axis=0)

    # Empty list for voxelwise variance
    var_img = []

    # Loop timepoints
    for tp in range(data.shape[0]):

        # Voxelwise variance between this timepoint and the median timepoint
        sample = np.stack([data[tp, ...], median_img], axis=0)
        var = np.var(sample, axis=0)

        # Store
        var_img.append(var)

    # Stack variance image
    vw_variance = np.stack(var_img, axis=0)

    # Normalise by mean voxel intensity across entire dataset
    vw_variance = vw_variance / data.mean()

    # Revert to original axis order
    vw_variance = np.moveaxis(vw_variance, 0, time_axis)

    # Return
    return vw_variance


# ==============
# THRESHOLD_TEST
# ==============


def threshold_test(vw_variance, summary_axis, threshold):
    '''
    Test sample-to-median variance against specified threshold.

    Accepts one or more summary axes along which to summarise variance before
    finding threshold violations.
    Example 1: for (x,y,z,t) data, axis=(0,1,2) will test across volumes
    Example 2: for (x,y,z,t) data, axis=(0,1) will test across z-axis slices
    Example 3: if axis=[] is unset, test voxelwise

    Inputs
        vw_variance  [array]  Voxelwise variance-to-mean array
        summary_axis [tuple]  One or more axes along which to perform test
        threshold    [scalar] Normalized variance threshold

    Outputs
        regressor   [array]  Voxelwise binary regressor of threshold violations
    '''

    # If axis is specified, take the mean variance along each axis
    if summary_axis:

        # Turn into a list
        if type(summary_axis) == int:
            summary_axis = (summary_axis)

        # Loop axes
        for i in summary_axis:
            insert = np.mean(vw_variance, axis=i, keepdims=True)
            vw_variance = np.repeat(insert, vw_variance.shape[i], axis=i)

    # Test each voxel against the threshold
    regressor = vw_variance > threshold

    # Return
    return regressor

# =====
# SCRUB
# =====


def scrub(data, regressor, time_axis):
    '''
    Perform variance-based scrubbing.

    Inputs
        data        [array ] N-dimensional voxelwise data array
        regressor   [array ] Voxelwise binary regressor of threshold violations
        time_axis   [scalar] Axis along which time is encoded
                             e.g. for (x,y,z,t) data, time_axis=3

    Outputs
        data_scrub  [array ] Scrubbed data array
    '''

    # Number of timepoints
    n_timepoints = data.shape[time_axis]

    # Move the time axis to the front
    q_data = np.moveaxis(data, time_axis, 0)
    q_regr = np.moveaxis(regressor, time_axis, 0)

    # Vectorise
    v_data = np.reshape(q_data, [n_timepoints, -1])
    v_regr = np.reshape(q_regr, [n_timepoints, -1])

    # Make a copy of the data
    data_scrub = v_data

    # Zero-pad either side the regressor along the time dimension
    v_regr = np.pad(
        v_regr,
        ((1, 1), (0, 0)),
        'constant',
        constant_values=(False)
    )

    # Loop voxels
    for voxel in range(v_regr.shape[1]):

        # This voxel's timeseries and regressor
        ts = v_data[:, voxel]
        reg = v_regr[:, voxel]

        # Locate timepoints to remove
        _, fp = find_peaks(reg, width=1)
        peaks = fp['left_bases'].astype(int)
        widths = fp['widths'].astype(int)

        # The peak 'left base' is the first non-peak point, so we want to
        # shift it by one to the right to ensure it's the index for the
        # first reject volume
        # ... however, we also padded the array with zeros, so we need to
        # shift the peak indices back to the lefy by one step as well
        # In summary, we should shift by one to the right (+1) and by one
        # to the right (-1), which cancel out

        # Loop peaks
        for p in range(len(peaks)):

            # Bad timepoint window
            window = np.arange(peaks[p], peaks[p] + widths[p])

            # Timepoints before and after window
            prev = window[0] - 1
            post = window[-1] + 1

            # Average volumes before and after window, while dealing
            # with window edges

            # If both left- and right-side edges are available,
            # average them
            if prev >= 0 and post < n_timepoints:
                insert = np.mean([ts[prev], ts[post]])

            # If the left-side edge is at the start of the run,
            # take the single volume after the peak
            elif prev < 0 and post < n_timepoints:
                insert = ts[post]

            # If the right-side edge is after the end of the run,
            # take the single volume before the peak
            elif prev >= 0 and post >= n_timepoints:
                insert = ts[prev]

            # If the entire timeseries is flagged, replace with
            # the median timepoint
            elif len(window) == n_timepoints:
                insert = np.median(ts)

            # If both conditions are violated, it means we are excluding
            # the entire run, and something has gone horribly wrong
            else:
                raise TypeError(
                    'Error: entire timecourse being excluded during scrubbing.'
                )

            # Plug window edge average into scrubbed data
            data_scrub[window, voxel] = insert

    # Reshape and revert to original axis order
    data_scrub = np.reshape(data_scrub, q_data.shape)
    data_scrub = np.moveaxis(data_scrub, 0, time_axis)

    # Return
    return data_scrub

# Done
#
