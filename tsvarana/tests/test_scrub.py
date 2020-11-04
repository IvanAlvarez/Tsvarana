# test_scrub.py
#
# test tsvarana scrubbing functions.
#
# Ivan Alvarez
# University of California, Berkeley

# =========
# LIBRARIES
# =========

# Libraries
import numpy as np

# Project dependencies
import tsvarana

# ====
# TEST
# ====

# Variance analysis instance, with arbitrary parameters
varana = tsvarana.classes.varana()
varana.slice_axis = 2
varana.time_axis = 3
varana.var_threshold = 0.1

# Generate dummy data with (x,y,z,t) dimensions
data = np.random.rand(10, 10, 10, 100)

# Test voxel-wise scrubbing
def test_scrubbing_voxel():

    # Run scrubbing
    varana.spatial_unit = 'voxel'
    varana.scrub_oneshot(data)

    # Output is a numpy array
    assert type(varana.data_scrub) == np.ndarray

    # Outputs have the same size as input data
    assert varana.data_scrub.shape == data.shape

    # Output is non-zero
    assert varana.data_scrub.sum() != 0

# Test slice-wise scrubbing
def test_detection_slice():

    # Run scrubbing
    varana.spatial_unit = 'slice'
    varana.scrub_oneshot(data)

    # Output is a numpy array
    assert type(varana.data_scrub) == np.ndarray

    # Outputs have the same size as input data
    assert varana.data_scrub.shape == data.shape

    # Output is non-zero
    assert varana.data_scrub.sum() != 0


# Test volume-wise scrubbing
def test_detection_volume():

    # Run scrubbing
    varana.spatial_unit = 'volume'
    varana.scrub_oneshot(data)

    # Output is a numpy array
    assert type(varana.data_scrub) == np.ndarray

    # Outputs have the same size as input data
    assert varana.data_scrub.shape == data.shape

    # Output is non-zero
    assert varana.data_scrub.sum() != 0

# Done
#
