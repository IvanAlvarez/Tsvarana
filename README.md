# Tsvarana

## About

**Tsvarana** performs (t)ime(s)eries (var)iance (ana)lysis for fMRI data, written in Python 3. It is a diagnostic tool intended to detect abnormal fluctuations in MRI signals, that you may wish to remove from further analysis.

The logic behind Tsvarana is based on a simple observation: abnormal signal intensities in fMRI data caused by non-physiological sources of noise stand out by being very different from the median signal intensity across a timeseries. A well-designed fMRI experiment will elicit BOLD signal fluctuations in the order of 1-4% signal change, with changes outside this range likely attributable to non-physiological sources of noise. Thus, by computing the voxelwise variance between signal intensity at every timepoint against the median signal intensity, we can detect abnormal voxels, slices or volumes for further inspection or removal.

Tsvarana is a spiritual successor to [tsdiffana](http://imaging.mrc-cbu.cam.ac.uk/imaging/DataDiagnostics), written by [Matthew Brett](https://github.com/matthew-brett). The two tools differ in some important aspects. First, signal assessment is carried out by comparing the signal variance in the time domain against the median signal amplitude. This approach is preferable to a sliding window approach, as it is more robust to cases of sustained abnormal intensities spanning consecutive timepoints. Second, timepoint removal or 'scrubbing' is performed iteratively. The iteration algorithm is defined as follows; (a) check all timepoint-to-median variances against a user-defined maximum variance threhold, (b) remove all timepoints failing the test, (c) replace removed timepoints with the mean of the first preceeding and first following retained timepoints, where available. Steps (a)-(c) are repeated until no further timepoints are marked for removal.

Tsvarana is experimental software and is provided with no warranty of any kind. 

## Installation

Install with `pip`

```
pip install tsvarana
```

Tsvarana has the following dependencies: [NumPy](https://numpy.org/), [SciPy](https://www.scipy.org/), [Bokeh](https://docs.bokeh.org/en/latest/index.html), [Nibabel](https://nipy.org/nibabel/)

## Usage

There are two ways to use Tsvarana. To perform a basic timeseries variance analysis and scrubbing, you can invoke tsvarana from the shell with

```bash
python -m tsvarana --data <4d_nifti>
```

Alternatively, you can use the tsvarana library from within a Python environment

```python
import tsvarana
```

See below for a step-by-step tutorial.

## Tutorial

```python
# Load library
import tsvarana

# Start by loading a 4D BOLD timeseries to the workspace. We will use the nibabel library for this
# This example dataset contains (x,y,z,t) dimensions
import nibabel as nib
header = nib.load('my_4D_data.nii.gz')
data = header.get_fdata()

# Define a variance analysis object
varana = tsvarana.classes.varana()

# First, we will define the spatial unit. Variance will be calculated at the specified spatial level, 
# which can be 'voxel', 'slice' or 'volume'. If slice is selected, you must specify the dimension 
# axis along which slices are taken
# For our example dataset with (x,y,z,t) dimensions, we'll pick slices along the z dimension
varana.spatial_unit = 'slice'
varana.slice_axis = 2

# We can also modify the axis along which time is stored
# In our example of (x,y,z,t) data, that will be the 3rd axis
varana.time_axis = 3

# Next, define the variance threshold, expressed in normalised variance units
# A value in the range of 5-10 is a reasonable starting point for fMRI data
# Note this threshold must be selected while considering the nature of your data acquisition
# protocol, and the type of signal abnormalities you wish to detect
varana.var_threshold = 5

# Perform diagnostics
# Calculate the timepoint-to-median variance using the settings specified above, and compare the
# empirical normalised variance against the previously-specified variance threshold
varana.detect(data)

# Plot the resulting variance diagnostics
tsvarana.plot_diagnostic(varana, show=True)

# Perform iterative scrubbing
# This step iterates the timepoint removal algorithm, until no timepoints display normalised
# variance-to-median above the specified threshold. Note that timepoints removed are replaced
# with the mean of the first valid preceeding and first valid following timepoint. If ony one
# is valid, a copy of that timepoint is used for replacement
varana.scrub_iterative(data)

# Plot every step of the diagnostic variance calculation
# This will create a HTML page, containing one figure for each iteration pass
tsvarana.plot_diagnostic(varana, outfile='variance.html')

# Plot every step of the binary thresholding
# As above, This will make one figure for each iteration pass
tsvarana.plot_regressor(varana, outfile='regressors.html')

# We can also obtain a regressor matrix, with all timepoints excluded flagged as 1s and timepoints
# that were never excluded as 0s
regressor = varana.get_final_regressor()

# Finally, we pull out the scrubbed timeseries data, and save it to a NIFTI file
data_scrub = varana.get_data_scrub()
img = nib.Nifti1Image(data_scrub, header.affine)
nib.save(img, 'my_scrubbed_data.nii.gz')
```

## Development

Tsvarana was created and maintained by [Ivan Alvarez](https://www.ivanalvarez.me/). To see the code or report a bug, please visit the [GitHub repository](https://github.com/IvanAlvarez/tsvarana). 