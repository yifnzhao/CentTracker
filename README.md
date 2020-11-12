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


### Install MATLAB packages
TODO:REDA (if there is installation/requirments for matlab scripts that you use.)

### Install Fiji
Detailed instructions can be found [here](https://imagej.net/Fiji). The version used for our experiments is [REDA: could you fill this in?].




<a name="usage"></a>
## 3 Usage

<a name="registration"></a>
### Module 1: Registration
#### 1. Create a x-y translation matrix.
- Detailed instructions for single movie: [relative path to be added].
- Detailed instructions for batch mode: [relative path to be added].
- TODO: REDA

#### 2. Register
- For single movie, a jupyter notebook with detailed instructions can be found [here](/src/singlemovie.ipynb).
- For batch mode, a jupyter notebook with detailed instructions can be found [here](/src/batchmode.ipynb).

<a name="tracking"></a>
### Module 2: Tracking
- TrackMate is our recommended software. Detailed installation and usage instructions can be found [here](https://imagej.net/TrackMate)
- TODO: REDA (maybe you can describe the trackmate parameters that you used a little bit?)

<a name="tpc"></a>
### Module 3: Track pair classification
- For single movie, a jupyter notebook with detailed instructions can be found [here](/src/singlemovie.ipynb).
- For batch mode, a jupyter notebook with detailed instructions can be found [here](/src/batchmode.ipynb).


<a name="scoring"></a>
### Module 4: Cell scoring
- TODO: REDA

<a name="trainable"></a>
## 4 The trainable option
- TODO: REDA, YIFAN


_________________
[OLD STUFF]
- Module 1 and 2: For step-to-step movie registration instructions, read the doc [here](https://github.com/yifnzhao/CENTRACKER/blob/master/how-to-register.md).
- Example usage for movie registration and track pairing can be found [here](https://github.com/yifnzhao/CENTRACKER/blob/master/src/register%20and%20pair.ipynb).
- Module 3: Example usage for classifier dataset preparation and training can be found [here](https://github.com/yifnzhao/CENTRACKER/blob/master/src/Dataset%20preparation%20and%20classifier%20training.ipynb).
- Module 4
