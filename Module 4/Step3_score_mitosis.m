% Plot each spindle length versus time (frames) for each cell and record
% the first and last frame of congression (i.e. first frame where spindle
% length hits ~mean length during congression and last frame before
% anaphase spindle elongation. Using these frames, calculate the duration
% of congression and the average spindle length during congression. Using
% the Celloutput structure from Scoremymito_import_and_align_cent_tracks.m as input.

% Before running this script use the CropCells macro in ImageJ to crop out
% each tracked cell. 
quest = {'Before running this script use the CropCells macro in ImageJ to crop out each tracked cell.';
    'This script allows you to score NEBD and the start and end of congression by clicking on a graph of spindle length versus time for each cell.';
    'Position the cross hairs and click to select the nearest x-coordinate (i.e. frame) for NEBD, congression start (CongS) and congression end (CongE), in that order.';
    'If an event occurs before or after the end of the timelapse (e.g. before frame 1 or after frame 80), click to the left or right of the graph, respectively.';
    'If the graph is unclear, click any button to open a cropped, max projection of the cell in question.';
    'You will be prompted to enter a frame for CongS and CongE and these values will then be displayed on the graph to guide your selection using the cross hairs.';
    'If you make a mistake, take note of the cell and continue scoring.'};
answer = questdlg(quest,'Welcome to Scoremymito','continue','continue');

% Because the fileList was generated before these tifs
% and ROI lists were made, it is neccessary to regenerate the fileList
fileList = getAllFiles(folder);
% Find all the .tif files in 'fileList'
boo = strfind(fileList,'tif');
%cellfun Apply function to each cell in cell array
%TF = isempty(A) returns logical 1 (true) if A is an empty array and logical 0 (false) otherwise.
foo = find(~cellfun('isempty', boo));
Tiff_fileList = fileList(foo, 1);


A = exist('Celloutput');
if A ~= 1
    error('No Celloutput variable in the work space');
else
    [~,kk] = size(Celloutput);
    for j = 1:1:kk
        Celloutput(j).scoring = NaN(1,3);
    end
    for j = 1:1:kk
        % Define limits of x-axis
        xstart = min(Celloutput(j).meas(:,1));
        firstframe = xstart;
        xstop = max(Celloutput(j).meas(:,1));
        % Ideally the x-axis would be roughly the same scale for all graphs
        % (i.e. the same number of time points, since spreading different
        % numbers of time points over the same length x-axis can distort the curves
        % and bias/complicate the scoring)
        xrange = xstop - xstart;
        if xrange < 79
            xstart = round(xstart + xrange/2) - 40;
            xstop = round(xstop - xrange/2) + 40;
        end
        % Create figure full screen
        figure1 = figure('units','normalized','outerposition',[0 0 1 1]);
        % Create axes
        % sets the x-axis tick values 
        axes1 = axes('Parent',figure1,'XTick',[xstart:2:xstop],'XGrid','on');
        box(axes1,'on');
        hold(axes1,'all');
        % Create plot - frames/spindle length
        X1 = Celloutput(j).meas(:,1);
        Y1 = Celloutput(j).meas(:,3);
        plot(X1,Y1,'Marker','o','Color',[0 0 1]);
        % Add title
        title({Celloutput(j).gonad;Celloutput(j).cell},'Interpreter','none');
        xlabel('Frames')
        ylabel('Mitotic spindle length')
        % Increase height of y-axis so that graphs are not cut off
        axis([xstart xstop 1 11]);
        % Add line at time = 0 for visual aid in scoring
        yL = get(gca,'YLim');
        line([0 0],yL,'Color','g','LineWidth',2);
        % Add label to graph with cell name
        annotation(figure1,'textbox',...
        [0.15 0.8 0.2 0.04],...
        'String',['Celloutput index ' num2str(j) '/' num2str(kk)],...
        'FontSize',16,...
        'FitBoxToText','off');
        % Show most recent graph window
        shg;
        
        % Add step to open max projection of each cell if graph is
        % challenging to interpret. If user clicks mouse, script proceeds
        % with scoring from graph. If user clicks button, script opens
        % corresponding image file to allow use to compare image to graph.
        
        w = waitforbuttonpress;
        if w == 1   
            gonad = Celloutput(j).gonad;
            cellID = Celloutput(j).cell;
            id = strcat(gonad,'_',cellID);
            boo = strfind(Tiff_fileList,id);
            foo = find(~cellfun('isempty', boo));
            file = Tiff_fileList{foo};
            [stack, img_read] = tiffread2(file); % stack is a structure with the px values for each tiff in stack.data. img_read = number of images in stack
            % Convert stack.date into multidimensional array
            [~, n] = size(stack);
            [aa, bb] = size(stack(1).data);
            stack_dbl = NaN(aa,bb,n);
            for m = 1:1:n
                stack_dbl(:,:,m) = double(stack(m).data);
            end
            max_val = max(max(max(stack_dbl)));
            min_val = min(min(min(stack_dbl)));
            stack_dbl = stack_dbl-min_val;
            outstack = uint16(65535*stack_dbl/max_val);
            Hh = implay(outstack);
            moo = Hh.Parent.CurrentAxes.Position;
            noo = [moo(1)-moo(3) moo(2)-moo(4) 3*moo(3) 3*moo(4)];
            Hh.Parent.CurrentAxes.Position = noo;
            % User inputs frame value corresponding to congression start
            % and stop, as assessed from image file. If not possible to
            % score --> enter NaN;
             prompt = {'Enter frame corresponding to NEBD :','Enter frame corresponding to congression start :','Enter frame corresponding to congression end :'};
            dlgtitle = 'Input';
            dims = [1 35];
            definput = {'NaN','NaN','NaN'};
            opts.WindowStyle = 'normal';
            answer = inputdlg(prompt,dlgtitle,dims,definput,opts);
            figure(Hh.Parent) % Brings implay window to front
            NEBD = str2num(cell2mat(answer(1,1)));
            CongS = str2num(cell2mat(answer(2,1)));             
            CongE = str2num(cell2mat(answer(3,1)));
            close(Hh);
            figure(figure1)
            if ~isnan(NEBD)
                line([NEBD NEBD],yL,'Color','g');
            end
            if ~isnan(CongS)
                line([CongS CongS],yL,'Color','r');
            end
            if ~isnan(CongE)
                line([CongE CongE],yL,'Color','m');
            end
        end

        % This allows each cell to be scored by clicking on the graph
        % generated above
        
        % Identify congression start = first frame where spindle length <= mean 
        % length during congression and congression end = last frame of congression prior to 
        % rapid/anaphase spindle elongation.
        
        % Click on the graph using the cross hairs as close to the correct
        % x-coordinates as possible. Script will round x-value clicked on
        % to the nearest integar.
% % %          
        [x1,y1] = ginput(1);
        text(x1,y1,'NEBD');
        x(1) = round(x1);
        
        
        [x2,y2] = ginput(1);
        text(x2,y2,'CongS');
        x(2) = round(x2);
        
        
        [x3,y3] = ginput(1);
        %text(x3,y3,'CongE'); Won't display since executed after the click
        %and after last selection, plot is closed.
        x(3) = round(x3);
% % %         
        % x(1) = NEBD, if possible to discern from spindle length plot
        % x(2) = start of congression
        % x(3) = end of congression
   
        
        % If the start of congression occurred before the first frame of
        % the image acquisition and the end of congression occurred after
        % the last frame of the image acquisition (i.e. the cell was
        % arrested in mitosis for the entire image acquisition), click
        % outside of the figure plot to the left, first, and then to the
        % right.
        
        % If the start of congression occurred before the first frame of the
        % image acquisition, click outside of the figure plot to the left.

        % If the end of congression occurred after the last frame of the
        % image acquisition, click outside of the figure plot to the right.
        
        % If both the start of congression and the end of congression
        % occurred before the first frame of the image acquisition (i.e.
        % the cell was in anaphase or later at time = 0), click 2x outside 
        % of the figure plot to the left.

        % If both the start of congression and the end of congression
        % occurred after the last frame of the image acquisition (i.e.
        % the cell was still in prophase at last image frame), click 2x outside 
        % of the figure plot to the right.
        
        if x(2) < xstart
            x(2) = NaN;
        end
        if x(2) > xstop
            x(2) = 5000;
        end
        if x(3) > xstop
            x(3)=NaN;
        end
        if x(3) < xstart
            x(3) = -5000;
        end
        if x(1) < xstart || x(1) > xstop
            x(1) = NaN;
        end
        
        % This will give 6 possible configurations for x: 
        % [x(2) x(3)] = full congression
        % [NaN, x(3)] = no start, end OK
        % [5000, NaN] = start and end after acquisition end/cell in
        % prophase
        % [x(2), NaN] = start OK, no end
        % [NaN, -5000] = start and end before acquisition start/cell in
        % anaphase/telophase
        % [NaN, NaN] = start before acquisition start and end after
        % acquisition end/cell arrested for entire acquisition
  
        % add congression end/start values to Celloutput
        Fs = x(2);
        Fe = x(3);
        nebd = x(1);
        Celloutput(j).scoring(1,1) = Fs;
        Celloutput(j).scoring(1,2) = Fe;
        Celloutput(j).scoring(1,3) = nebd;
        close(figure1);
    end
end

 clearvars -except Celloutput Germlineoutput Tiff_fileList folder