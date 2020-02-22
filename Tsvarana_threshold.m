function Regressor = Tsvarana_threshold(Varana, Opts)
% Regressor = Tsvarana_threshold(Varana, Opts)
%
% Inputs
%   Varana         [struct]
%   Opts           [struct] 
%
% Outputs
%   Regressor      [vector] Binary bad volume regressor
%
% Changelog
%
% 21/02/2020    Written
%
% Ivan Alvarez
% University of California, Berkeley
%

%% Main

% Normalised volume-to-volume variance
VolumeNorm = Varana.VolumeVar / mean(Varana.MeanSignal);

% Pre-append the mean, as the first volume cannot be compared to a
% preceeding volume
VolumeNorm = cat(1, mean(VolumeNorm, 1), VolumeNorm);

% Find volumes that violate the threshold
Regressor = VolumeNorm > Opts.Threshold;

% Done
%