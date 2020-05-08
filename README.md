# CENTRACKER: A trainable software for automated centrosome tracking and pairing in *C. elegans* germline
This document describes the steps to track and pair centrosomes from time-lapse movies of *C. elegans* germline. *Note: the trainable option is currently under developemnt.*

### Materials and Requirements
- your germline movie (.tiff)
- [FIJI](https://imagej.net/Fiji) (with [TrackMate](https://imagej.net/TrackMate) installed)
- python 3.6 ([Anaconda](https://www.anaconda.com/) recommended) with the following packages installed: 
  - numpy
  - pandas
  - scipy
  - matplotlib
  - skimage
  - pickle

### Usage

1. Process the movie through TrackMate. This step is to use TrackMate's LoG spot detector to get Euclidiean coordinates of all spots with relatively high quality. The TrackMate automated script for batch processing is currently development. **TODO**

2. To initialize, run:
```
# declare paths
originalMovie = 'u_germline.tif'
originalXML = 'u_germline.xml'
path = '/Users/yifan/Dropbox/ZYF/dev/GitHub/centracker/data/2018-01-16_GSC_L4_L4440_RNAi/'

# initialize centracker
myTracker = centracker(path,originalXML,originalMovie)
```

2. To generate a translation matrix, run:
```
transmat = myTracker.generateTransMat(maxIntensityRatio=0.2,maxDistPair=11,
                    maxDistPairCenter=11,method='Mode',searchRange=2.0)
```


Alternatively, you can generate a trans_mat using semi-automated method as described [here](https://github.com/gerhold-lab/Semi-automated-GSC-registration/). The Semi-automated-GSC-registration repostisoty contains detailed tutorials and source code.

3. Once you have the translation matrix, to register the movie, run:
```
metadata = myTracker.register(transmat,highres=True,compress=1,pad=True)
```
4. Process the registered movie through TrackMate again. This time we want to use TrackMate's LAP tracker to generate tracks of relatively high quality. The TrackMate automated script for batch processing is currently development. **TODO**

5. Once you have the trackmate output xml for the registered movie, to pair the tracks, run:
```
registeredXML = 'r_germline.xml'
myTracker.pair(registeredXML,maxdist=11,maxcongdist=4,minoverlap=10,dim=None) 
```
All done!
