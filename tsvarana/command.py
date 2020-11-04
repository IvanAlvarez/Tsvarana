# command.py
#
# functions for running tsvarana as a shell command.
#
# Ivan Alvarez
# University of California, Berkeley

# =========
# LIBRARIES
# =========

# Libraries
import nibabel as nib

# Project dependencies
import tsvarana

# ===============
# DEFAULT_ROUTINE
# ===============


def default_routine(args):
    '''
    Default tsvarana routine.

    Inputs
      args.data           [string] A 4D NIFTI fila
      args.spatial_unit   [string] Calculate mean variance along the specified
                                   spatial unit: 'voxel', 'slice' or 'volume'
      args.slice_axis     [scalar] Axis long which slice dimension is defined
                                   default for (x,y,z,t) data is slice_axis=2
      args.time_axis      [scalar] Axis long which time is stored
                                   default for (x,y,z,t) data is time_axis=3
      args.var_threshold  [scalar] Normalised variance threshold for scrubbing
      args.one_shot       [ bool ] If True, perform a single scrub iteration
      args.output         [string] Basename for output files
    '''

    # Read NIFTI data file
    header = nib.load(args.data)
    data = header.get_fdata()

    # Define the variance analysis model
    varana = tsvarana.classes.varana()

    # Define model settings
    varana.spatial_unit = args.spatial_unit
    varana.slice_axis = args.slice_axis
    varana.time_axis = args.time_axis
    varana.var_threshold = args.var_threshold

    # Perform single-shot variance analysis and scrubbing
    if args.one_shot:
        varana.scrub_oneshot(data)

    # Perform iterative variance analysis and scrubbing
    else:
        varana.scrub_iterative(data)

    # Plot & save diagnostics
    tsvarana.plot.diagnostic(varana, outfile=args.output + '_variance.html')

    # Plot & save regressors
    tsvarana.plot.regressor(varana, outfile=args.output + '_regressor.html')

    # Save final regressor matrix as NIFTI
    final_regressor = varana.get_final_regressor()
    img = nib.Nifti1Image(final_regressor, header.affine)
    nib.save(img, args.output + '_regressor.nii.gz')

    # Save scrubbed timeseries data as NIFTI
    data_scrub = varana.get_data_scrub()
    img = nib.Nifti1Image(data_scrub, header.affine)
    nib.save(img, args.output + '_scrubbed.nii.gz')

# Done
#
