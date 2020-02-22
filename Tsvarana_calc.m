function Varana = Tsvarana_calc(Data, Opts)
% Varana = Tsvarana_calc(Data, Opts)
%
% Inputs
%   Data        [matrix] M x N x P x Time, image intensity matrix
%   Opts        [struct] 
%
% Outputs
%   Varana         [struct]
%     .MeanSignal  [vector] Mean signal intensity for each volume
%     .VolumeVar   [vector] Mean volume-to-volume variance
%     .SliceVar    [vector] Mean volume-to-volume variance, across slices
%
% Changelog
%
% 15/02/2020    Written
% 21/02/2020    Now taking options structure as input
%
% Ivan Alvarez
% University of California, Berkeley
%

%% Data dimensionality parsing

% Assign slice dimension index
switch Opts.SliceDim
    case 'x'
        SliceIdx = 1;
    case 'y'
        SliceIdx = 2;
    case 'z'
        SliceIdx = 3;
    otherwise
        error('Not a valid slice direction.');
end

% Which dimensions to collapse to get slice mean
DimCollapse = [1, 2, 3];
DimCollapse = DimCollapse(DimCollapse ~= SliceIdx);

% Number of volumes & slices in data
Nvol = size(Data, 4);
Nslice = size(Data, SliceIdx);

%% Main

% Mean signal intensity across voxels
MeanSignal = squeeze(mean(Data, [1,2,3]));

% Empty variable for volume-to-volume variance, across slices
SliceVar = nan(Nvol - 1, Nslice);

% Loop volume pairs
for i = 1 : Nvol - 1
    
    % 2-volume sample
    Sample = Data(:, :, :, i : i + 1);
    
    % Voxelwise variance between timepoints
    % Note we are calculating the population variance, and not the
    % normalised sample mean, which is why we are not using the
    % built-in function var()
    VowelwiseVar = diff(Sample, [], 4) .^ 2;
    
    % Mean variance across voxels, for each slice
    SliceVar(i, :) = mean(VowelwiseVar, DimCollapse);
end

% Average across slices
VolumeVar = mean(SliceVar, 2);

% Store in structure
Varana = struct;
Varana.MeanSignal = MeanSignal;
Varana.SliceVar = SliceVar;
Varana.VolumeVar = VolumeVar;

% Done
%