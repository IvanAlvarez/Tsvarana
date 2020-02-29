function Tsvarana(Nifti, Opts)
% Tsvarana(Nifti, [Opts])
%
% Inputs
%   Nifti           [string] 4-dimensional NIFTI file
%   Opts            [struct]
%    .SliceDim      [string] Slice dimension (x,y,z)
%    .Threshold     [scalar] Scaled mean variance threshold
%    .Scrub         [logica] Apply volume nulling iteratively
%    .Plot          [logica] Create plot
%    .OutputName    [string] Basename for output files
%    .SaveMat       [logica] Save variance analysis as .mat file
%    .SaveCsv       [logica] Save variance analysis as .csv files
%    .SaveScrub     [logica] Save scrubbed timeseries as NIFTI file
%    .SavePlot      [logica] Save plot figure
%
% MRI timeseries variance analysis in MATLAB.
% Estimates the volume-to-volume variance in a 4D NIFTI dataset, and outputs 
% relevant metrics and plots. If requested, volumes with variance above a 
% user-specified threshold are nulled by replacement with the average of the 
% previous and following threshold-compliant volumes. This procedure is carried 
% out iteratively, until the variance threshold is satisfied. Optional outputs
% are volume-to-volume variance parameters (.mat, .csv), variance plots (.png), 
% and the scrubbed timeseries (.nii.gz).
% 
% Based on Matthew Brett's tsdiffana:
% http://imaging.mrc-cbu.cam.ac.uk/imaging/DataDiagnostics
%
% Requirements
%  * MATLAB R2017b (v9.3.0) or later
%  * MATLAB Image Processing Toolbox
%  * MATLAB Signal Processing Toolbox
%
% Changelog
%
% 16/02/2020    Written
% 18/02/2020    Added scrubbing
% 21/02/2020    Added threshold-dependent iteration
%
% Ivan Alvarez
% University of California, Berkeley

%% Parse inputs

% Defaults
if nargin < 1
    
    % Launch GUI for user to select NIFTI data
    Nifti = uigetfile('*.nii.gz');
end
if nargin < 2
    
    % Default options
    Opts.SliceDim = 'z';
    Opts.Threshold = 5;
    Opts.Scrub = true;
    Opts.Plot = true;
    Opts.OutputName = [];
    Opts.SaveMat = true;
    Opts.SaveCsv = true;
    Opts.SaveScrub = true;
    Opts.SavePlot = true;
end

% If no output name specified, use input filename
if isempty(Opts.OutputName)
    
    % Perform twice, in case the input is a compressed NIFTI (.nii.gz)
    [~, Opts.OutputName] = fileparts(Nifti);
    [~, Opts.OutputName] = fileparts(Opts.OutputName);
end

%% Load

% Load image data
Header = niftiinfo(Nifti);
Data = double(niftiread(Nifti));

%% Main

% Make a copy for scrubbing
ScrubbedData = Data;

% Empty variable for bad volumes regressor
BadVolumes = false(size(Data, 4), 1);

% Empty plot handle
FigureHandle = [];

% Iteration counter
Iter = 0;

% Loop
while Inf
    
    % Update iteration counter
    Iter = Iter + 1;
    
    % Calculate variance
    Varana = Tsvarana_calc(ScrubbedData, Opts);
        
    % Generate plot
    FigureHandle = Tsvarana_plot(Varana, Opts);
        
    % Define bad volume regressor
    Regressor = Tsvarana_threshold(Varana, Opts);
    
    % Update cummulative list of bad volumes
    BadVolumes = BadVolumes + Regressor;
    
    % Scrub data
    if Opts.Scrub
        ScrubbedData = Tsvarana_scrub(ScrubbedData, Regressor);
    end    
    
    % If scrubbing was requested, iterate until the variance threshold is 
    % no longer violated
    if Opts.Scrub
        
        % Save this iteration
        Tsvarana_save(Varana, FigureHandle, Opts, Iter);
        
        % Break out
        if sum(Regressor) == 0
            break
        end
    end
    
    % If Scrubbing was not requested, accept the first-pass
    % variance calculation, save out and quit
    if ~Opts.Scrub

        % Save
        Tsvarana_save(Varana, FigureHandle, Opts);
        
        % Break out
        break
    end
end

%% Save

% Save bad volumes regressor (MAT)
if Opts.SaveMat
    save([Opts.OutputName '_volumereg.mat'], 'BadVolumes');
end

% Save bad volumes regressor (CSV)
if Opts.SaveCsv
    writematrix(BadVolumes, [Opts.OutputName '_volumereg.csv']);
end

% Save scrubbed data as NIFTI file
if Opts.SaveScrub
      
    % Convert image to original data type
    ScrubbedData = cast(ScrubbedData, Header.Datatype);
    
    % Write
    niftiwrite(ScrubbedData, [Opts.OutputName '_scrub'], Header, 'Compressed', true);
end

% Done
%