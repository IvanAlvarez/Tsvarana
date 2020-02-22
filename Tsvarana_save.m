function Tsvarana_save(Varana, FigureHandle, Opts, Iter)
% Tsvarana_save(Varana, FigureHandle, Opts, [Iter])
%
% Inputs
%   Varana         [struct]
%   FigureHandle   [struct]
%   Opts           [struct]
%   Iter           [scalar] Iteration number, optional
%
% Outputs
%   MAT, CSV and PNG files
%
% Changelog
%
% 18/02/2020    Written
% 21/02/2020    Tidied up input/output
%
% Ivan Alvarez
% University of California, Berkeley
%

%% Parse inputs

% Defaults
if nargin < 4
    Iter = [];
end

% Define iteration suffix
if isempty(Iter)
    Suffix = [];
else
    Suffix = ['_' num2str(Iter)];
end
    
% Save variance analysis as .mat file
if Opts.SaveMat
    save([Opts.OutputName '_varana' Suffix '.mat'], 'Varana');
end

% Save variance analysis as .csv files 
if Opts.SaveCsv
    writematrix(Varana.MeanSignal, [Opts.OutputName '_meansignal' Suffix '.csv']);
    writematrix(Varana.VolumeVar, [Opts.OutputName '_volumevar' Suffix '.csv']);
    writematrix(Varana.SliceVar, [Opts.OutputName '_slicevar' Suffix '.csv']);
end

% Save plot figure
if Opts.SavePlot
    saveas(FigureHandle, [Opts.OutputName '_varana' Suffix '.png']);    
end

% Done
%