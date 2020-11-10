% Plot each spindle length versus time (frames) for each cell
% Plot corresponding Fs and Fe scored in Scoremymito_scoremitosisALL.m
% Plot fitted curves obtained by Scoremymito_scoremitosisALL.m

A = exist('Celloutput');
if A ~= 1
    error('No Celloutput variable in the work space');
else
    [~,kk] = size(Celloutput);
    scoreORfiterrors = {};
    for j = 1:1:kk
        % Define limits of x-axis
        xstart = min(Celloutput(j).meas(:,2));
        firstframe = xstart;
        xstop = max(Celloutput(j).meas(:,2));
        Frate = abs(nanmean(Celloutput(j).meas(1:end-1,2)-Celloutput(j).meas(2:end,2)));
        % Ideally the x-axis would be roughly the same scale for all graphs
        % (i.e. the same number of time points, since spreading different
        % numbers of time points over the same length x-axis can distort the curves
        % and bias/complicate the scoring)
        xrange = xstop - xstart;
        if xrange < 2370
            xstart = round(xstart + xrange/2) - 1185;
            xstop = round(xstop - xrange/2) + 1185;
        end
        % Create figure full screen
        figure1 = figure('units','normalized','outerposition',[0 0 1 1]);
        % Create axes
        % sets the x-axis tick values 
        axes1 = axes('Parent',figure1,'XTick',[xstart:round(Frate*2):xstop],'XGrid','on');
        box(axes1,'on');
        hold(axes1,'all');
        % Create plot - frames/spindle length
        X1 = Celloutput(j).meas(:,2);
        Y1 = Celloutput(j).meas(:,3);
        plot(X1,Y1,'Marker','o','Color',[0 0 1]);
        % Add title
        title({Celloutput(j).gonad;Celloutput(j).cell},'Interpreter','none');
        xlabel('Time (sec)')
        ylabel('Mitotic spindle length')
        axis([xstart xstop 1 11]);
        % Add vertical lines corresponding to scoring
        Frs = Celloutput(j).scoring(1,1);
        Fre = Celloutput(j).scoring(1,2);
        FrNEBD = Celloutput(j).scoring(1,3);
        Ts = (Frs-1)*Frate;
        Te = (Fre-1)*Frate;
        TNEBD = (FrNEBD-1)*Frate;
        yL = get(gca,'YLim');
        line([Ts Ts],yL,'Color','m');
        line([Te Te],yL,'Color','g');
        line([TNEBD TNEBD],yL,'Color','b');
        line([0 0],yL,'Color','k','LineWidth',2);
        annotation(figure1,'textbox',...
            [0.15 0.8 0.2 0.04],...
            'String',['Celloutput index ' num2str(j) '/' num2str(kk)],...
            'FontSize',16,...
            'FitBoxToText','off');
        % create values to plot the fitted lines using the
        % coefficients from the 'fit' function
        % for NEBD to CongS (N):
        if ~isnan(Frs) && ~isnan(Fre)
            CoefN = Celloutput(j).scoring(2,1:2);
            CoefC = Celloutput(j).scoring(3,1:2);
            CoefA = Celloutput(j).scoring(4,1:2);
            xN = [Ts-240:30:Ts+120]';
            yN = CoefN(1,1)*xN+CoefN(1,2);
            % for congression (C):
            xC = [Ts-120:30:Te+120]';
            yC = CoefC(1,1)*xC+CoefC(1,2);
            % for CongE through anaphase (A):
            xA = [Te-120:30:Te+240]';
            yA = CoefA(1,1)*xA+CoefA(1,2);
            hold on
            plot(xN,yN,'r');
            plot(xC,yC,'r');
            plot(xA,yA,'r');
        end
        %Show most recent graph window
        shg;
        % If fits are an accurate representation of data, click a mouse button
        % Otherwise, press any key and you can modify your scoring
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
            NEBD = (str2num(cell2mat(answer(1,1)))-1)*Frate;
            CongS = (str2num(cell2mat(answer(2,1)))-1)*Frate;             
            CongE = (str2num(cell2mat(answer(3,1)))-1)*Frate;
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
            x(1) = round(x1/Frate)+1;
            [x2,y2] = ginput(1);
            text(x2,y2,'CongS');
            x(2) = round(x2/Frate)+1;
            [x3,y3] = ginput(1);
        %text(x3,y3,'CongE'); Won't display since executed after the click
        %and after last selection, plot is closed.
            x(3) = round(x3/Frate)+1;
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
        else
            close(figure1);
        end
    end
end

    % calculate the duration of congression for cells for which both the
    % start and end of congression occurred during the image acquisition
    [~,kk] = size(Celloutput);
    for j = 1:1:kk
        [row, col] = size(Celloutput(j).meas);
        Fs = Celloutput(j).scoring(1,1);
        Fe = Celloutput(j).scoring(1,2);
        Frate = abs(nanmean(Celloutput(j).meas(1:end-1,2)-Celloutput(j).meas(2:end,2)));
        % To avoid using fits generated from previous cells, we need to see
        % if these variables exist and, if so, delete them.
        clearvars A C N
        % excludes cells where first or last frame of congression did not occur
        % during the image acquisition (i.e. fit will only be attempted on
        % cells where the full duration of congression was captured)
        if ~isnan(Fs) && ~isnan(Fe) && Fe ~= -5000 && Fs ~= 5000
            % nebd = nuclear envelop breakdown
            % cong = CONGRESSION
            % ana = ANAPHASE
            % Identify the frames used to calculate the regression lines
            % that will be used to calculate the duration of congression by their
            % intersection points
            Fsnebd = [Fs-3:1:Fs]';  
            Fscong = [Fs:1:Fe]'; 
            Fsana = [Fe:1:Fe+3]';
            % converts frames to time in seconds by pulling out
            % corresponding time values from column 2 of Celloutput.meas
            Tnebd = Celloutput(j).meas(Celloutput(j).meas(:,1)>=min(Fsnebd) & Celloutput(j).meas(:,1)<=max(Fsnebd),2);
            Tcong = Celloutput(j).meas(Celloutput(j).meas(:,1)>=min(Fscong) & Celloutput(j).meas(:,1)<=max(Fscong),2);
            Tana = Celloutput(j).meas(Celloutput(j).meas(:,1)>=min(Fsana) & Celloutput(j).meas(:,1)<=max(Fsana),2);
            % Identifies the spindle length for the frames of interest by pulling out
            % corresponding spindle length values from column 3 of Celloutput.meas
            SLnebd = Celloutput(j).meas(Celloutput(j).meas(:,1)>=min(Fsnebd) & Celloutput(j).meas(:,1)<=max(Fsnebd),3);
            SLcong = Celloutput(j).meas(Celloutput(j).meas(:,1)>=min(Fscong) & Celloutput(j).meas(:,1)<=max(Fscong),3);
            SLana = Celloutput(j).meas(Celloutput(j).meas(:,1)>=min(Fsana) & Celloutput(j).meas(:,1)<=max(Fsana),3);
            
            % need to remove any NaNs before trying 'fit'
            Tnebd = Tnebd(~isnan(SLnebd));
            Tcong = Tcong(~isnan(SLcong));
            Tana = Tana(~isnan(SLana));
            
            SLnebd = SLnebd(~isnan(SLnebd));
            SLcong = SLcong(~isnan(SLcong));
            SLana = SLana(~isnan(SLana));
            
            % Try to fit nebd, congression and anaphase time points with a linear polynomial curve
            % If the fit fails, the script displays spindle length vs frame
            % for the cell in question and allows the user to correct any
            % scoring errors that may be affecting the fit
            try
                N = fit(Tnebd,SLnebd,'poly1');
                C = fit(Tcong,SLcong,'poly1');
                A = fit(Tana,SLana,'poly1');
            catch
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
                % Add line at time = 0 for visual aid in scoring and lines
                % showing the originally selected CongS and CongE
                yL = get(gca,'YLim');
                line([0 0],yL,'Color','k','LineWidth',2);
                line([Fs Fs],yL,'Color','g');
                line([Fe Fe],yL,'Color','g');
                % Add label to graph with cell name
                annotation(figure1,'textbox',...
                [0.15 0.8 0.2 0.04],...
                'String',['Celloutput index ' num2str(j) '/' num2str(kk)],...
                'FontSize',16,...
                'FitBoxToText','off');
                % Show most recent graph window and ask user how to proceed
                shg;
                answer = questdlg('Would you like to:', ...
                'Correct Scoring', ...
                'Use scored values','Rescore','Rescore');
                switch answer
                    case 'Use scored values'
                        % If scored values are accurate and changing them is
                        % unlikely to produce a better fit, then...
                        DurC = (Fe-Fs)*Frate;
                        Celloutput(j).scoring(2,1:2) = NaN;
                        Celloutput(j).scoring(3,1:2) = NaN;
                        Celloutput(j).scoring(4,1:2) = NaN;
                        % To save the calculated congression start and end points:
                        Celloutput(j).scoring(5,1) = NaN;
                        Celloutput(j).scoring(5,2) = NaN;
                    case 'Rescore'
                        % This allows each cell to be scored by clicking on
                        % the graph. User rescores CongS and CongE
                        answer = questdlg('Rescore CongS and CongE (NOT NEBD) by clicking on the plot. Click outside the plot to NaN either value or both', ...
                        'Correct Scoring','Continue','Continue');
                        [x1,y1] = ginput(1);
                        text(x1,y1,'CongS');
                        x(1) = round(x1);
        
                        [x2,y2] = ginput(1);
                        text(x2,y2,'CongE');
                        x(2) = round(x2);
                        
                        if x(1) < xstart || x(1) > xstop
                            x(1) = NaN;
                        end
                
                        if x(2) < xstart || x(2) > xstop
                            x(2) = NaN;
                        end
                        
                        Fs = x(1);
                        Fe = x(2);
                        
                        Celloutput(j).scoring(1,1) = Fs;
                        Celloutput(j).scoring(1,2) = Fe;
                        
                        % If user did not NaN out CongS or CongE, retry the
                        % fitting
                        if ~isnan(Fs) && ~isnan(Fe)
                            % Identify the frames used to calculate the regression lines
                            % that will be used to calculate the duration of congression by their
                            % intersection points
                            Fsnebd = [Fs-3:1:Fs]';  
                            Fscong = [Fs:1:Fe]'; 
                            Fsana = [Fe:1:Fe+3]';
                            % converts frames to time in seconds by pulling out
                            % corresponding time values from column 2 of Celloutput.meas
                            Tnebd = Celloutput(j).meas(Celloutput(j).meas(:,1)>=min(Fsnebd) & Celloutput(j).meas(:,1)<=max(Fsnebd),2);
                            Tcong = Celloutput(j).meas(Celloutput(j).meas(:,1)>=min(Fscong) & Celloutput(j).meas(:,1)<=max(Fscong),2);
                            Tana = Celloutput(j).meas(Celloutput(j).meas(:,1)>=min(Fsana) & Celloutput(j).meas(:,1)<=max(Fsana),2);
                            % Identifies the spindle length for the frames of interest by pulling out
                            % corresponding spindle length values from column 3 of Celloutput.meas
                            SLnebd = Celloutput(j).meas(Celloutput(j).meas(:,1)>=min(Fsnebd) & Celloutput(j).meas(:,1)<=max(Fsnebd),3);
                            SLcong = Celloutput(j).meas(Celloutput(j).meas(:,1)>=min(Fscong) & Celloutput(j).meas(:,1)<=max(Fscong),3);
                            SLana = Celloutput(j).meas(Celloutput(j).meas(:,1)>=min(Fsana) & Celloutput(j).meas(:,1)<=max(Fsana),3);
                            % need to remove any NaNs before trying 'fit'
                            Tnebd = Tnebd(~isnan(SLnebd));
                            Tcong = Tcong(~isnan(SLcong));
                            Tana = Tana(~isnan(SLana));
                            
                            SLnebd = SLnebd(~isnan(SLnebd));
                            SLcong = SLcong(~isnan(SLcong));
                            SLana = SLana(~isnan(SLana));
                            % Try to fit nebd, congression and anaphase time points with a linear polynomial curve
                            % If the fit fails, the script displays spindle length vs frame
                            % for the cell in question and allows the user to correct any
                            % scoring errors that may be affecting the fit
                            try
                                N = fit(Tnebd,SLnebd,'poly1');
                                C = fit(Tcong,SLcong,'poly1');
                                A = fit(Tana,SLana,'poly1');
                            catch
                                DurC = (Fe-Fs)*Frate;
                                Celloutput(j).scoring(2,1:2) = NaN;
                                Celloutput(j).scoring(3,1:2) = NaN;
                                Celloutput(j).scoring(4,1:2) = NaN;
                                % To save the calculated congression start and end points:
                                Celloutput(j).scoring(5,1) = NaN;
                                Celloutput(j).scoring(5,2) = NaN;
                            end
                        else
                            DurC = (Fe-Fs)*Frate;
                            Celloutput(j).scoring(2,1:2) = NaN;
                            Celloutput(j).scoring(3,1:2) = NaN;
                            Celloutput(j).scoring(4,1:2) = NaN;
                            % To save the calculated congression start and end points:
                            Celloutput(j).scoring(5,1) = NaN;
                            Celloutput(j).scoring(5,2) = NaN;
                        end
                end
                close(figure1);
            end
            if exist('A') && exist('C') && exist('N')
                % Pull out the values of the coefficients for each fit
                CoefN = coeffvalues(N);
                CoefC = coeffvalues(C);
                CoefA = coeffvalues(A);
                
                % find the x-position of the intersection points of the nebd and congression
                % and the congression and anaphase lines by => ax+b=cx+d <=> x(a-c)=d-b <=> x=(d-b)/c-a)
                NCx = (CoefC(1,2)-CoefN(1,2))/(CoefN(1,1)-CoefC(1,1));
                CAx = (CoefA(1,2)-CoefC(1,2))/(CoefC(1,1)-CoefA(1,1));
                
                % at this step, we will check to see whether the calculated
                % points of intersaction deviate substantially from the
                % user-scored CongS and CongE. If so, we will display the
                % spindle length vs frame plot, with the fitted lines, manually selected CongS and CongE
                % and ask the user to decide whether to replace the selected
                % values and redo the fit, or
                % ignore the fit and use the selected values
                
                % convert scored frame values for CongS and CongE into time
                Ts = (Celloutput(j).scoring(1,1)-1)*Frate;
                Te = (Celloutput(j).scoring(1,2)-1)*Frate;
                
                if abs(Ts-NCx) > 60 || abs(Te-CAx) > 60
                    % Define limits of x-axis using time rather than frames
                    xstart = min(Celloutput(j).meas(:,2));
                    firstframe = xstart;
                    xstop = max(Celloutput(j).meas(:,2));
                    % Ideally the x-axis would be roughly the same scale for all graphs
                    % (i.e. the same number of time points, since spreading different
                    % numbers of time points over the same length x-axis can distort the curves
                    % and bias/complicate the scoring)
                    xrange = xstop - xstart;
                    if xrange < 2370
                        xstart = round(xstart + xrange/2) - 1185;
                        xstop = round(xstop - xrange/2) + 1185;
                    end
                    % Create figure full screen
                    figure1 = figure('units','normalized','outerposition',[0 0 1 1]);
                    % Create axes
                    % sets the x-axis tick values
                    axes1 = axes('Parent',figure1,'XTick',[xstart:round(Frate*2):xstop],'XGrid','on');
                    box(axes1,'on');
                    hold(axes1,'all');
                    % Create plot - frames/spindle length
                    X1 = Celloutput(j).meas(:,2);
                    Y1 = Celloutput(j).meas(:,3);
                    plot(X1,Y1,'Marker','o','Color',[0 0 1]);
                    % Add title
                    title({Celloutput(j).gonad;Celloutput(j).cell},'Interpreter','none');
                    xlabel('Time (sec)')
                    ylabel('Mitotic spindle length')
                    % Increase height of y-axis so that graphs are not cut off
                    axis([xstart xstop 1 11]);
                    % Add lines to graph to indicate scored CongS and CongE
                    yL = get(gca,'YLim');
                    line([0 0],yL,'Color','k','LineWidth',2);
                    line([Ts Ts],yL,'Color','g');
                    line([Te Te],yL,'Color','g');
                    % Add label to graph with cell name
                    annotation(figure1,'textbox',...
                        [0.15 0.8 0.2 0.04],...
                        'String',['Celloutput index ' num2str(j) '/' num2str(kk)],...
                        'FontSize',16,...
                        'FitBoxToText','off');
                    % create values to plot the fitted lines using the
                    % coefficients from the 'fit' function
                    % for NEBD to CongS (N):
                    xN = [Ts-240:30:Ts+120]';
                    yN = CoefN(1,1)*xN+CoefN(1,2);
                    % for congression (C):
                    xC = [Ts-120:30:Te+120]';
                    yC = CoefC(1,1)*xC+CoefC(1,2);
                    % for CongE through anaphase (A):
                    xA = [Te-120:30:Te+240]';
                    yA = CoefA(1,1)*xA+CoefA(1,2);
                    hold on
                    plot(xN,yN,'r');
                    plot(xC,yC,'r');
                    plot(xA,yA,'r');
                    % Show most recent graph window
                    shg;
                    answer = questdlg('Would you like to:', ...
                        'Correct Scoring', ...
                        'Use fit values','Use scored values','Rescore','Rescore');
                    switch answer
                        case 'Use fit values'
                            DurC = CAx-NCx;
                            Celloutput(j).scoring(2,1:2) = CoefN;
                            Celloutput(j).scoring(3,1:2) = CoefC;
                            Celloutput(j).scoring(4,1:2) = CoefA;
                            % To save the calculated congression start and end points:
                            Celloutput(j).scoring(5,1) = NCx;
                            Celloutput(j).scoring(5,2) = CAx;
                        case 'Use scored values'
                            DurC = Te-Ts;
                            Celloutput(j).scoring(2,1:2) = NaN;
                            Celloutput(j).scoring(3,1:2) = NaN;
                            Celloutput(j).scoring(4,1:2) = NaN;
                            % To save the calculated congression start and end points:
                            Celloutput(j).scoring(5,1) = NaN;
                            Celloutput(j).scoring(5,2) = NaN;
                        case 'Rescore'
                            clearvars A N C
                            [x1,y1] = ginput(1);
                            text(x1,y1,'CongS');
                            Ts = round(x1);
                            
                            [x2,y2] = ginput(1);
                            text(x2,y2,'CongE');
                            Te = round(x2);
                            % replace the original values in Celloutput with
                            % these newly scored values
                            Celloutput(j).scoring(1,1) = round(Ts/Frate)+1;
                            Celloutput(j).scoring(1,2) = round(Te/Frate)+1;
                            % repeat the fitting steps and reassess
                            % close(figure1);
                            Fs = Celloutput(j).scoring(1,1);
                            Fe = Celloutput(j).scoring(1,2);
                            
                            Fsnebd = [Fs-3:1:Fs]';
                            Fscong = [Fs:1:Fe]';
                            Fsana = [Fe:1:Fe+3]';
                            % converts frames to time in seconds by pulling out
                            % corresponding time values from column 2 of Celloutput.meas
                            Tnebd = Celloutput(j).meas(Celloutput(j).meas(:,1)>=min(Fsnebd) & Celloutput(j).meas(:,1)<=max(Fsnebd),2);
                            Tcong = Celloutput(j).meas(Celloutput(j).meas(:,1)>=min(Fscong) & Celloutput(j).meas(:,1)<=max(Fscong),2);
                            Tana = Celloutput(j).meas(Celloutput(j).meas(:,1)>=min(Fsana) & Celloutput(j).meas(:,1)<=max(Fsana),2);
                            % Identifies the spindle length for the frames of interest by pulling out
                            % corresponding spindle length values from column 3 of Celloutput.meas
                            SLnebd = Celloutput(j).meas(Celloutput(j).meas(:,1)>=min(Fsnebd) & Celloutput(j).meas(:,1)<=max(Fsnebd),3);
                            SLcong = Celloutput(j).meas(Celloutput(j).meas(:,1)>=min(Fscong) & Celloutput(j).meas(:,1)<=max(Fscong),3);
                            SLana = Celloutput(j).meas(Celloutput(j).meas(:,1)>=min(Fsana) & Celloutput(j).meas(:,1)<=max(Fsana),3);
                            
                            % need to remove any NaNs before trying 'fit'
                            Tnebd = Tnebd(~isnan(SLnebd));
                            Tcong = Tcong(~isnan(SLcong));
                            Tana = Tana(~isnan(SLana));
                            
                            SLnebd = SLnebd(~isnan(SLnebd));
                            SLcong = SLcong(~isnan(SLcong));
                            SLana = SLana(~isnan(SLana));
                            % Try to fit nebd, congression and anaphase time points with a linear polynomial curve
                            % If the fit fails, the script displays spindle length vs frame
                            % for the cell in question and allows the user to correct any
                            % scoring errors that may be affecting the fit
                            try
                                N = fit(Tnebd,SLnebd,'poly1');
                                C = fit(Tcong,SLcong,'poly1');
                                A = fit(Tana,SLana,'poly1');
                            catch
                                % If the new fit fails, use rescored values
                                DurC = Te-Ts;
                                Celloutput(j).scoring(2,1:2) = NaN;
                                Celloutput(j).scoring(3,1:2) = NaN;
                                Celloutput(j).scoring(4,1:2) = NaN;
                                % To save the calculated congression start and end points:
                                Celloutput(j).scoring(5,1) = NaN;
                                Celloutput(j).scoring(5,2) = NaN;
                            end
                            
                            if exist('A') && exist('C') && exist('N')
                                % Pull out the values of the coefficients for each fit
                                CoefN = coeffvalues(N);
                                CoefC = coeffvalues(C);
                                CoefA = coeffvalues(A);
                                
                                % find the x-position of the intersection points of the nebd and congression
                                % and the congression and anaphase lines by => ax+b=cx+d <=> x(a-c)=d-b <=> x=(d-b)/c-a)
                                NCx = (CoefC(1,2)-CoefN(1,2))/(CoefN(1,1)-CoefC(1,1));
                                CAx = (CoefA(1,2)-CoefC(1,2))/(CoefC(1,1)-CoefA(1,1));
                                % if large discrepencies persist, just use the
                                % scored values
                                if abs(Ts-NCx) > 60 || abs(Te-CAx) > 60
                                    DurC = Te-Ts;
                                    Celloutput(j).scoring(2,1:2) = NaN;
                                    Celloutput(j).scoring(3,1:2) = NaN;
                                    Celloutput(j).scoring(4,1:2) = NaN;
                                    % To save the calculated congression start and end points:
                                    Celloutput(j).scoring(5,1) = NaN;
                                    Celloutput(j).scoring(5,2) = NaN;
                                else
                                    DurC = CAx-NCx;
                                    Celloutput(j).scoring(2,1:2) = CoefN;
                                    Celloutput(j).scoring(3,1:2) = CoefC;
                                    Celloutput(j).scoring(4,1:2) = CoefA;
                                    % To save the calculated congression start and end points:
                                    Celloutput(j).scoring(5,1) = NCx;
                                    Celloutput(j).scoring(5,2) = CAx;
                                end
                            end
                    end
                    close(figure1);
                else
                    DurC = CAx-NCx;
                    Celloutput(j).scoring(2,1:2) = CoefN;
                    Celloutput(j).scoring(3,1:2) = CoefC;
                    Celloutput(j).scoring(4,1:2) = CoefA;
                    % To save the calculated congression start and end points:
                    Celloutput(j).scoring(5,1) = NCx;
                    Celloutput(j).scoring(5,2) = CAx;
                end
            end
            Celloutput(j).out(1,1) = DurC; % duration of mitosis/congression in seconds
            Celloutput(j).out(1,2) = nanmean(SLcong); % mean spindle length during mitosis/congression
            Celloutput(j).out(1,3) = nanstd(SLcong); % standard deviation of spindle length during mitosis/congression
        else
            Celloutput(j).out(1,1:3) = NaN;
        end
        % removed script for spindle and rachis angle calculations and this
        % should be included in a separate script.
    end
    
    % You will want to change this to extract the values that you are
    % interested in, i.e. expand it to include spindle angle etc.
    
    [~,kk] = size(Celloutput); % in case kk was reassigned
    
    % Compile all the measurements that you want to split by gonad/worm by
    % looping through the Celloutput structure and pulling out the
    % following:
    NEBD = NaN(kk,1);
    CongStart = NaN(kk,1);
    CongEnd = NaN(kk,1);
    NEBDtoAna = NaN(kk,1);
    DurCong = NaN(kk,1);
    meanSpinLength = NaN(kk,1);
    STdevSpinLength = NaN(kk,1);
    SpinElongationRate = NaN(kk,1);

    Framerate = NaN(kk,1);
    Gonads = cell(kk,1);
    Cells = cell(kk,1);
    
    % Germlineoutput should be a structure with a size (BB) equal the number
    % of original Trackmate files, i.e. the number of gonads with tracked
    % cells. Germlineoutput is generated by the script
    % Scoremymito_import_and_align_cent_tracks.m. Use the values in
    % Germlineoutput.gonad and Germlineoutput.lastframe to determine
    % whether cells with either the start or end of congression missing
    % (i.e. before t0 or after tlast, respectively) are delayed.
    B = exist('Germlineoutput');
    if B ~= 1
        error('No Germlineoutput variable in the work space');
    else 
        [~, BB] = size(Germlineoutput);
        gonadIDs = cell(BB,1);
        TotalFrames = NaN(BB,1);
        for i = 1:1:BB
            gonadIDs{i,1} = Germlineoutput(i).gonad;
            TotalFrames(i,1) = Germlineoutput(i).lastframe;
        end
    
        for i = 1:1:kk
            % Calculate frame rate using all timepoints to avoid using skipped
            % frames where time value = NaN
            Framerate(i,1) = abs(nanmean(Celloutput(i).meas(1:end-1,2)-Celloutput(i).meas(2:end,2)));
            Gonads{i,1} = Celloutput(i).gonad;
            Cells{i,1} = Celloutput(i).cell;
        
            NEBD(i,1) = Celloutput(i).scoring(1,3) * Framerate(i,1);
        
            if isnan(Celloutput(i).scoring(1,1)) || Celloutput(i).scoring(1,1) == 5000 || isnan(Celloutput(i).scoring(1,2)) || Celloutput(i).scoring(1,2) == -5000
                CongStart(i,1) = Celloutput(i).scoring(1,1);
                CongEnd(i,1) = Celloutput(i).scoring(1,2);
                % Converts scored frames, i.e. not NaN or +/-5000, into seconds
                if CongStart(i,1) ~= 5000 && ~isnan(CongStart(i,1))
                    CongStart(i,1) = CongStart(i,1) * Framerate(i,1);
                else
                    CongStart(i,1) = NaN;
                end
                if CongEnd(i,1) ~= -5000 && ~isnan(CongEnd(i,1))
                    CongEnd(i,1) = CongEnd(i,1) * Framerate(i,1);
                else
                    CongEnd(i,1) = NaN;
                end
            else
                CongStart(i,1) = Celloutput(i).scoring(5,1);
                CongEnd(i,1) = Celloutput(i).scoring(5,2);
            end
        
            NEBDtoAna(i,1) = CongEnd(i,1) - NEBD(i,1);
            DurCong(i,1) = CongEnd(i,1) - CongStart(i,1);
        
%             if isnan(CongStart(i,1)) && isnan(CongEnd(i,1))
%                 DurCong(i,1) = 1;
%             elseif CongStart(i,1) == -5000 || CongEnd(i,1) == 5000
%                 DurCong(i,1) = NaN;
%             elseif ~isnan(CongStart(i,1)) && CongStart(i,1) ~= -5000 && isnan(CongEnd(i,1))
%                 % Identify delayed cells as those that are in "congression" for
%                 % more than 12 minutes
%                 gonad = Gonads{i,1};
%                 boo = find(strcmp(gonadIDs, gonad));
%                 LT = TotalFrames(boo) * Framerate(i,1);
%                 if LT - CongStart(i,1) > 720
%                     DurCong(i,1) = 2;
%                 else
%                     DurCong(i,1) = NaN;
%                 end
%             elseif isnan(CongStart(i,1)) && CongEnd(i,1) ~= 5000 && ~isnan(CongEnd(i,1))
%                 if CongEnd(i,1) > 720
%                     DurCong(i,1) = 2;
%                 else
%                     DurCong(i,1) = NaN;
%                 end
%             else
%                 DurCong(i,1) = CongEnd(i,1) - CongStart(i,1);
%             end
 
            meanSpinLength(i,1) = Celloutput(i).out(1,2);
            STdevSpinLength(i,1) = Celloutput(i).out(1,3);
            if DurCong(i,1) ~= 1 && DurCong(i,1) ~= 2 && ~isnan(DurCong(i,1))
                SpinElongationRate(i,1) =  Celloutput(i).scoring(4,1);
            else
                SpinElongationRate(i,1) = NaN;
            end
 % If the start/end of congression was defined by the fit, it takes
 % the fitted value, otherwise the scored values are used. CongStart
 % and CongEnd will have time in seconds or NaN, if occured before or
 % after start of acquisition. CongStart will have NaNs for cells where 
 % congression started before or after the start/end of image acquisition
        end
        for j = 1:1:BB
            worm = Germlineoutput(j).gonad;
            boo = strcmp(Gonads, worm);
            Germlineoutput(j).Framerate = max(Framerate(boo,1));
            Germlineoutput(j).columnIdx = {'NEBD' 'Congression start', 'Congression end' 'NEBD to AO' 'Congression duration' 'Mean spindle length'...
                'Spindle length StDev' 'Anaphase elongation (um/s)'};
            Germlineoutput(j).meas(:,1) = NEBD(boo,1);
            Germlineoutput(j).meas(:,2) = CongStart(boo,1);
            Germlineoutput(j).meas(:,3) = CongEnd(boo,1);
            Germlineoutput(j).meas(:,4) = NEBDtoAna(boo,1);
            Germlineoutput(j).meas(:,5) = DurCong(boo,1);
            Germlineoutput(j).meas(:,6) = meanSpinLength(boo,1);
            Germlineoutput(j).meas(:,7) = STdevSpinLength(boo,1);
            Germlineoutput(j).meas(:,8) = SpinElongationRate(boo,1);
            % count the number of mitotic cells per frame for each gonad
            maxframe = TotalFrames(j);
            FrameIndx = [1:1:maxframe]';
            gonadIndx = find(boo);
            bob = NaN(length(FrameIndx),length(gonadIndx));
            for cc = 1:1:length(gonadIndx)
                celltoadd = Celloutput(gonadIndx(cc)).meas(:,1);
                for dd = 1:1:length(FrameIndx)
                    if sum(FrameIndx(dd) == celltoadd) == 1;
                        bob(dd,cc) = celltoadd(FrameIndx(dd) == celltoadd);
                    end
                end
            end
            cellcountperframe = sum(~isnan(bob),2);
            Germlineoutput(j).mitocounts = cellcountperframe;
        end
    end

 clearvars -except Celloutput Germlineoutput Tiff_fileList