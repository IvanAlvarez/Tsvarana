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
import pytest
from unittest import TestCase

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


class TestDetection(TestCase):
    '''
    Test detection functions for unit errors
    '''

    # Test voxel-wise detection
    def test_detection_voxel():
        varana.spatial_unit = 'voxel'
        varana.detect(data)
        assert varana.variance[0].shape == data.shape

    # Test slice-wise detection
    def test_detection_slice():
        varana.spatial_unit = 'slice'
        varana.detect(data)
        assert varana.variance[0].shape == data.shape

    # Test volume-wise detection
    def test_detection_volume():
        varana.spatial_unit = 'volume'
        varana.detect(data)
        assert varana.variance[0].shape == data.shape

    # Catch
    with pytest.raises(ValueError):
        varana.detect(data)

# Done
#
