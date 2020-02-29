# Tsvarana
### About
MRI timeseries variance analysis in MATLAB.

Estimates the volume-to-volume variance in a 4D NIFTI dataset, and outputs relevant metrics and plots. If requested, volumes with variance above a user-specified threshold are nulled by replacement with the average of the previous and following threshold-compliant volumes. This procedure is carried out iteratively, until the variance threshold is satisfied. Optional outputs are volume-to-volume variance parameters (.mat, .csv), variance plots (.png), and the scrubbed timeseries (.nii.gz).

Based on Matthew Brett's tool [tsdiffana](http://imaging.mrc-cbu.cam.ac.uk/imaging/DataDiagnostics).

### Requirements

  * MATLAB R2017b (v9.3.0) or later
  * MATLAB Image Processing Toolbox
  * MATLAB Signal Processing Toolbox

### How to

To use with the default parameters, simply run:

```matlab
Tsvarana
```

And use the graphical interface to select a 4D NIFTI dataset.

To specify the desired parameters, build a structure with the following fields:

```matlab
Opts = struct;
Opts.SliceDim 		% [string] Slice dimension (x,y,z)
Opts.Threshold    % [scalar] Scaled mean variance threshold
Opts.Scrub        % [logica] Apply volume nulling iteratively
Opts.Plot         % [logica] Create plot
Opts.OutputName   % [string] Basename for output files
Opts.SaveMat      % [logica] Save variance analysis as .mat file
Opts.SaveCsv      % [logica] Save variance analysis as .csv files
Opts.SaveScrub    % [logica] Save scrubbed timeseries as NIFTI file
Opts.SavePlot     % [logica] Save plot figure
```

And pass the options to the Tsvarana function, along with the desired 4D NIFTI dataset

```matlab
Tsvarana('my_nifti.nii.gz', Opts)
```

### License
v1.0.0
28 February 2020

Ivan Alvarez
University of California, Berkeley