function FigureHandle = Tsvarana_plot(Varana, Opts)
% FigureHandle = Tsvarana_plot(Varana, Opts)
%
% Inputs
%   Varana         [struct]
%     .MeanSignal  [vector] Mean signal intensity for each volume
%     .VolumeVar   [vector] Mean volume-to-volume variance
%     .SliceVar    [vector] Mean volume-to-volume variance, across slices
%   Opts           [struct] 
%
% Output
%   FigureHandle   [struct] Figure handle

% Changelog
%
% 15/02/2020    Written
% 28/02/2020    Figure hidden
%
% Ivan Alvarez
% University of California, Berkeley
%

%% Figure handling

% Start new figure
FigureHandle = figure;

% Rebrand and hide
FigureHandle.Visible = 'off';
FigureHandle.Name = 'Tsvarana';

%% Plot #1
% Mean volume-to-volume variance

% Start
subplot(3,1,1);
hold on;

% Define data
PlotData = Varana.VolumeVar / mean(Varana.MeanSignal);

% Plot
h = plot(PlotData);

% Add threshold line
hl = line([1, length(PlotData)], [Opts.Threshold, Opts.Threshold]);

% Tidy plot
h.Color = [0, 0, 0];
h.LineWidth = 2;

% Tidy line
hl.Color = [1, 0, 0];
hl.LineWidth = 3;
hl.LineStyle = ':';

% Tidy axes
ax = gca;
ax.XLim = [1, length(PlotData)];
ax.XLabel.String = 'Volume (TR)';
ax.YLabel.String = 'Normalised variance';
ax.FontSize = 14;
ax.XLabel.FontSize = 14;
ax.YLabel.FontSize = 14;
ax.Box = 'on';
ax.TickLength = [0, 0];

% Finish
hold off;

%% Plot #2
% Mean volume-to-volume variance, across slices

% Start
subplot(3,1,2);
hold on;

% Define data
PlotData = Varana.SliceVar / mean(Varana.MeanSignal);
PlotData = PlotData';

% Plot
h = imagesc(PlotData);
hb = colorbar;

% Tidy plot
ax = gca;
colormap(jet);
ax.XLim = [1, size(PlotData, 2)];
ax.YLim = [1, size(PlotData, 1)];
ax.XLabel.String = 'Volume (TR)';
ax.YLabel.String = 'Slice';
hb.Label.String = 'Normalised variance';
ax.FontSize = 14;
ax.XLabel.FontSize = 14;
ax.YLabel.FontSize = 14;
hb.FontSize = 14;
hb.Label.FontSize = 14;
ax.Box = 'on';
ax.TickLength = [0, 0];

% Finish
hold off;

%% Plot #3 
% Mean voxel intensity

% Start
subplot(3,1,3);
hold on;

% Define data
PlotData = Varana.MeanSignal / mean(Varana.MeanSignal);

% Plot
h = plot(PlotData);

% Tidy plot
h.Color = [0, 0, 0];
h.LineWidth = 2;

% Tidy axis
ax = gca;
ax.XLim = [1, length(PlotData)];
ax.XLabel.String = 'Volume (TR)';
ax.YLabel.String = 'Normalised mean signal intensity';
ax.FontSize = 14;
ax.XLabel.FontSize = 14;
ax.YLabel.FontSize = 14;
ax.Box = 'on';
ax.TickLength = [0, 0];

% Finish
hold off;

% Done
%