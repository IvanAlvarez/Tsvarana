function ScrubbedData = Tsvarana_scrub(Data, Regressor)
% ScrubbedData = Tsvarana_calc(Data, Regressor)
%
% Inputs
%   Data           [matrix] M x N x P x Time, image intensity matrix
%   Regressor      [vector] Binary bad volume regressor
%
% Outputs
%   ScrubbedData   [matrix]  M x N x P x Time
%
% Changelog
%
% 18/02/2020    Written
% 21/02/2020    Tidied up input/output
%
% Ivan Alvarez
% University of California, Berkeley
%

%% Main

% Make a copy of the data
ScrubbedData = Data;

% Zero-padding
Reg = [0; single(Regressor(:)); 0];

% Locate bad volumes
[~, Location, Width, ~] = findpeaks(Reg);

% De-pad indices
Location = Location - 1;

% Loop peaks
for i = 1 : length(Location)
    
    % Bad volumes window
    Window = Location(i) : Location(i) + Width(i) - 1;
    
    % Volumes before and after window
    Prev = Window(1) - 1;
    Post = Window(end) + 1;
    
    % Deal with window edges
    if Prev < 1
        Prev = [];
    end
    if Post > length(Regressor)
        Post = [];
    end
    
    % Average volumes before and after window
    Insert = Data(:, :, :, [Prev, Post]);
    Insert = mean(Insert, 4);
    Insert = repmat(Insert, [1, 1, 1, Width(i)]);
    
    % Insert into location of scrubbed window
    ScrubbedData(:, :, :, Window) = Insert;
end

% Done
%