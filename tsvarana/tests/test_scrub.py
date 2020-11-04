# test_scrub.py
#
# test tsvarana scrub functions.
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


class TestScrub(TestCase):
    '''
    Test scrub functions for unit errors
    '''

    # Test voxel-wise scrubbing
    def test_scrub_voxel():
        varana.spatial_unit = 'voxel'
        varana.scrub_iterative(data)
        assert varana.data_scrub.shape == data.shape

    # Test slice-wise scrubbing
    def test_scrub_slice():
        varana.spatial_unit = 'slice'
        varana.scrub_iterative(data)
        assert varana.data_scrub.shape == data.shape

    # Test volume-wise scrubbing
    def test_scrub_volume():
        varana.spatial_unit = 'volume'
        varana.scrub_iterative(data)
        assert varana.data_scrub.shape == data.shape

    # Catch
    with pytest.raises(ValueError):
        varana.data_scrub([])

# Done
#
