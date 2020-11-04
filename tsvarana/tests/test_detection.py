# test_detection.py
#
# test tsvarana diagnosis functions.
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

# Test voxel-wise detection
def test_detection_voxel():

    # Run detection
    varana.spatial_unit = 'voxel'
    varana.detect(data)

    # Outputs are lists
    assert type(varana.variance) == list
    assert type(varana.regressor) == list

    # Outputs have the same size as input data
    assert varana.variance[0].shape == data.shape
    assert varana.regressor[0].shape == data.shape

    # Variance output is non-zero
    assert varana.variance[0].sum() != 0


# Test slice-wise detection
def test_detection_slice():

    # Run detection
    varana.spatial_unit = 'slice'
    varana.detect(data)

    # Outputs are lists
    assert type(varana.variance) == list
    assert type(varana.regressor) == list

    # Outputs have the same size as input data
    assert varana.variance[0].shape == data.shape
    assert varana.regressor[0].shape == data.shape

    # Variance output is non-zero
    assert varana.variance[0].sum() != 0


# Test volume-wise detection
def test_detection_volume():

    # Run detection
    varana.spatial_unit = 'volume'
    varana.detect(data)

    # Outputs are lists
    assert type(varana.variance) == list
    assert type(varana.regressor) == list

    # Outputs have the same size as input data
    assert varana.variance[0].shape == data.shape
    assert varana.regressor[0].shape == data.shape

    # Variance output is non-zero
    assert varana.variance[0].sum() != 0

# Done
#
