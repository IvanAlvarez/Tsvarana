# classes.py
#
# tsvarana class definitions.
#
# Ivan Alvarez
# University of California, Berkeley

# =========
# LIBRARIES
# =========

# Project dependencies
from tsvarana.core import (
    variance_calc,
    threshold_test,
    scrub
)
from tsvarana.utils import (
    parse_spatial_unit,
    regressor_final
)

# ======
# VARANA
# ======


class varana():
    '''
    Variance analysis class.
    '''

    def __init__(self,
                 spatial_unit='voxel',
                 slice_axis=2,
                 time_axis=3,
                 var_threshold=5):
        '''
        Parameters
            spatial_unit : string
                'voxel', 'slice' or 'volume'
            slice_axis : integer
                Axis long which the slice dimension is defined
                default for (x,y,z,t) data is slice_axis=2
            time_axis : integer
                Axis along which time is stored
                default for (x,y,z,t) data is time_axis=3
            var_threshold : scalar
                Normalised variance threshold
                default = 5
        '''

        # Set parameters
        self.spatial_unit = spatial_unit
        self.slice_axis = slice_axis
        self.time_axis = time_axis
        self.var_threshold = var_threshold

    def detect(self, data):
        '''
        Calculate timepoint-to-median variance using setting stored in _self_,
        then compared the empirical normalised variance against the variance
        threshold given

        Inputs
            data    [array ] N-dimensional voxelwise data array
        '''

        # Update summary axis
        self.summary_axis = parse_spatial_unit(
            self.spatial_unit,
            data.ndim,
            self.slice_axis,
            self.time_axis
        )

        # Variance calculation
        vw_variance = variance_calc(data, self.time_axis)

        # Threshold test
        regressor = threshold_test(
            vw_variance,
            self.summary_axis,
            self.var_threshold
        )

        # Store
        self.variance = [vw_variance]
        self.regressor = [regressor]

    def scrub_oneshot(self, data):
        '''
        Perform one-shot data scrubbing

        Inputs
            data    [array ] N-dimensional voxelwise data array
        '''

        # Run detection
        self.detect(data)

        # Scrubbing
        data_scrub = scrub(
            data,
            self.regressor[0],
            self.time_axis
        )

        # Store
        self.data_scrub = data_scrub

    def scrub_iterative(self, data):
        '''
        Perform iterative variance calculation and data scrubbing,
        until no timepoints get replaced.

        Inputs
            data    [array ] N-dimensional voxelwise data array
        '''

        # Empty lists
        var_iter = []
        reg_iter = []

        # Iteration counter
        counter = 0

        # Start infinite loop
        while True:

            # Update counter
            counter += 1

            # Message
            print('Iteration: ' + str(counter))

            # Run scrubbing
            self.scrub_oneshot(data)

            # Message
            print('Bad timepoints: ' + str(self.regressor[0].sum()))

            # Store voxelwise variance & regressor
            var_iter.append(self.variance[0])
            reg_iter.append(self.regressor[0])

            # Re-assigned scrubbed data as the input for the next iteration
            data = self.data_scrub

            # Exit clause
            if self.regressor[0].sum() == 0:
                break

        # Iterations finished, re-assign variance & regressor lists
        self.variance = var_iter
        self.regressor = reg_iter

    def get_variance(self):
        '''
        Return list of voxelwise variances, one per scrub iteration
        '''
        return self.variance

    def get_regressor(self):
        '''
        Return list of voxelwise regressors, one per scrub iteration
        '''
        return self.regressor

    def get_regressor_final(self):
        '''
        Return binary mask of all timepoints scrubbed across iterations
        '''
        return regressor_final(self.regressor)

    def get_data_scrub(self):
        '''
        Return final scrubbed data
        '''
        return self.data_scrub

# Done
#
