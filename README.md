# CENTRACKER: A trainable software for automated centrosome tracking and pairing in *C. elegans* germline
This document describes the steps to track and pair centrosomes from time-lapse movies of *C. elegans* germline. *Note: the trainable option is currently under developemnt.*

### Materials and Requirements
- your germline movie (.tiff)
- [FIJI](https://imagej.net/Fiji) (with [TrackMate](https://imagej.net/TrackMate) installed)
- python 3.6 ([Anaconda](https://www.anaconda.com/) recommended) with the following packages installed: 
  - [trackpy](http://soft-matter.github.io/trackpy/dev/installation.html)
  - numpy
  - pandas
  - scipy
  - matplotlib
  - skimage
  - pickle

### Usage

1. Process the movie through TrackMate. The trackmate xml should have the same name as the original movie, except for the extension (.xml instead of .tif). This step is to use TrackMate's LoG spot detector to get Euclidiean coordinates of all spots with relatively high quality. The TrackMate automated script for batch processing is currently development. **TODO**

2. Make sure your data folder only has the original movie and the corresponding xml file. There is no need to provide the file names. The script will automatically read all file names in the folder you provided. To initialize, run:
```
in_path = 'PATH/TO/YOUR/INPUTDATA/FOLDER'
out_path = 'PATH/TO/YOUR/OUTPUTDATA/FOLDER'
model_path = 'PATH/TO/YOUR/CENTRACKER/src/model/myModel.sav'
myTracker = centracker(in_path,out_path,model_path)
```

2. To generate a translation matrix, run:
```
transmat=myTracker.generateTransMat(maxIntensityRatio=0.2,maxDistPair=11,maxDistPairCenter=11,method='Mode',searchRange=2.0,tbb_ch=1)
```
Alternatively, you can generate a trans_mat using a semi-automated method as described [here](https://github.com/gerhold-lab/Semi-automated-GSC-registration/). The Semi-automated-GSC-registration repo contains a detailed walk-through and source code.

3. Once you have the translation matrix, to register the movie, run:
```
metadata=myTracker.register(transmat,highres=True,compress=1,pad=True)
```
4. Process the registered movie through TrackMate again. This time we want to use TrackMate's LAP tracker to generate tracks of relatively high quality. The TrackMate automated script for batch processing is currently development. **TODO**

5. Once you have the trackmate output xml for the registered movie, to pair the tracks, run:
```
myTracker.pair(maxdist=11,maxcongdist=4,minoverlap=10,dim=None)
```
All done!
