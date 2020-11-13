# CentTracker
A trainable, machine learning-based tool for large-scale analyses of intravital imaging of C. elegans germline stem cell mitosis.

The full description of CentTracker and its application on live imaging microscopy datasets are available in ... (to be added once on bioarxiv).

This repository includes detailed instructions for installation, requirements, demos for single movie as well as batch processing.



## Contents ##

1. [Pipeline overview](#overview)
2. [Installation](#installation)
3. [Usage](#usage)
  - [Module 1: Registration](#registration)
  - [Module 2: Tracking](#tracking)
  - [Module 3: Track pair classificatino](#tpc)
  - [Module 4: Cell soring](#scoring)
4. [The trainable option](#trainable)


<a name="overview"></a>
## 1 Pipeline overview
- TODO: add the model figure and caption from manuscript (REDA or YIFAN)

<a name="installation"></a>
## 2 Installation
### Clone this repository, either by GitHub desktop, direct download, or by entering the following in the terminal
```
$ wget https://github.com/yifnzhao/CentTracker/archive/master.zip
$ unzip master.zip
$ rm master.zip
$ cd CentTracker-master
```

### Install Conda
1. Install conda. Detailed installation instructions can be found [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/). Now, check if conda is installed and in your PATH by
  - Open a terminal client.
  - Enter ```conda -V``` into the terminal command line and press enter. If conda is installed you should see something like the following:
```
$ conda -V
conda 4.9.0
```
2. Create and activate a virtual environment, by entering
```
$ conda create -n "mitosis" python=3.8.5
$ conda activate mitosis
```

### Install python packages
After you have ```cd```'d to the CentTracker foler, simply enter
```pip install -r requirements.txt``` in the terminal


### Install MATLAB 2020b
https://www.mathworks.com/products/matlab.html

### Install Fiji
Detailed instructions can be found [here](https://imagej.net/Fiji). The version used for our experiments is 1.52v.


<a name="usage"></a>
## 3 Usage

<a name="registration"></a>
### Module 1: Registration
#### 1. Create a x-y translation matrix.
Pre-requisite:
Group your original movies that are under the same conditions in the same folder and assign each of them a folder labeled with their name without extension.
Example :
Your main folder : Controls
                      Subfolder : 
                         2018-01-16_GSC_L4_L4440_RNAi_1
		                            File : 2018-01-16_GSC_L4_L4440_RNAi_1.tif
		      Subfolder : 
                         2018-01-16_GSC_L4_L4440_RNAi_2
		                            File : 2018-01-16_GSC_L4_L4440_RNAi_2.tif
		      Subfolder : 
                         2018-01-16_GSC_L4_L4440_RNAi_2
	                            	File : 2018-01-16_GSC_L4_L4440_RNAi_1.tif	

1. Open Fiji, drag and drop automatedregistrationtool.ijm then run it.
2. First window will ask you for the original movies directory ( according to the example, it would be the “Controls” folder.
3. First movie in your folder will open and channels will be splitted if your movie has more than 1 channel, a window will then ask you to select the centrosomes channel.
4. A max z-projection of your movie will then be generated, ROI Manager will open and a window prompting “click when done tracking”, do not click on done until step 7 is done.
5. Look for a pair of prominently congressing centrosomes. You might need to watch the movie a few times to identify such a pair. But it gets very easy with a little practice.
6. At t = 0, draw a straight line in the middle of the two centrosomes that you identified in the previous step. This line should approximate the metaphase plate (see Figure 1). Then, enter "t" on your keyboard (shortcut for "Add" in ROI manager).
7. Go to the next time point. If the metaphase plate position changes, move your line accordingly using "->" or "<-" on your keyboard. Enter "t" to add the line. Repeat this step until the last time point is reached or the metaphase plate for this cell cannot be tracked accurately anymore then click on done.
8. A window will ask you if you need to "track an additional cell ?", click Yes if the metaphase plate tracking did not reach the last time point. Repeat then step 5 to 7 but starting at the last time point tracked and looking for a new pair of centrosomes. Repeat this step as long as you did not reach the last time point, there is no limit of additional cells then click on No for "track an additional cell ?".
![Figure 1](https://github.com/yifnzhao/Semi-automated-GSC-registration/blob/master/figures/Figure%202.png)


#### 2. Register
- To open a jupyter notebook, simply enter the following in the terminal
```
$ conda activate mitosis
$ jupyter notebook
```
which should open in your default web browser.

- For single movie, a jupyter notebook with detailed instructions can be found [here](/src/singlemovie.ipynb).
- For batch mode, a jupyter notebook with detailed instructions can be found [here](/src/batchmode.ipynb).

<a name="tracking"></a>
### Module 2: Tracking
- TrackMate is our recommended software. Detailed installation and usage instructions can be found [here](https://imagej.net/TrackMate).
1. Open Fiji, drag and drop automatedfixhyperstack.ijm then run it.
2. First window will ask you for the original movies directory (according to the example, it would be the “Controls” folder. At this stage each movie subfolder should contain the original movie, the registered movie starting with “r_” and a subfolder “roi”.
3. First original movie will open in the background to extract dimensions then registered movie will open with correct dimensions.
4. A window will then ask you to draw a rectangle around the border of your movie reducing the best possible the surrounding extra borders resulting from registration then click on Done.
5. A window asking to "generate a .xml using Trackmate" will prompt (do not click on done until step 5 completion) and Trackmate window will open, then click on next. Select LoG detector then click on next. Choose the channel of centrosomes. We used 2.5 microns for GSCs centrosomes estimated blob diameter and lowered the threshold until all centrosomes were detected (important step ! use button preview to ensure that all centrosomes were detected), it does no matter if some spurious spots were also detected. Click on next 6 times until linking max distance is asked. We used for GSCs centrosomes 2.7  microns for linking max distance, gap closing max distance and we used 2 for Gap-closing max frame gap. Click next 2 times until the display options window appear and then click on save and save the Trackmate output ( a .xml file) in same folder as your registered movie and ensure that that file is labeled the same as the registered movie.
5. Click on done when done generating the xml.


<a name="tpc"></a>
### Module 3: Track pair classification
- For single movie, a jupyter notebook with detailed instructions can be found [here](/notebooks/singlemovie.ipynb).
- For batch mode, a jupyter notebook with detailed instructions can be found [here](/notebooks/batchmode.ipynb).


<a name="scoring"></a>
### Module 4: Cell scoring
- TODO: REDA

<a name="trainable"></a>
## 4 The trainable option
- Step-to-step walkthrough can be found here: [here](/notebooks/trainable.ipynb).
- REDA: pls see the notebook above. There is one or two steps that need you to help me fill out.


_________________
[OLD STUFF]
- Module 1 and 2: For step-to-step movie registration instructions, read the doc [here](https://github.com/yifnzhao/CENTRACKER/blob/master/how-to-register.md).
- Example usage for movie registration and track pairing can be found [here](https://github.com/yifnzhao/CENTRACKER/blob/master/src/register%20and%20pair.ipynb).
- Module 3: Example usage for classifier dataset preparation and training can be found [here](https://github.com/yifnzhao/CENTRACKER/blob/master/src/Dataset%20preparation%20and%20classifier%20training.ipynb).
- Module 4
