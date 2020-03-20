# Semi-automated Centrosome Pairing

This document describes the steps to track and pair centrosomes from time-lapse movies of *C. elegans* germline.

#### Materials and Requirements
- a registered time-lapse tiff movie and its correponding translation matrix (i.e., the ROI csv files), see [this repository](https://github.com/gerhold-lab/Semi-automated-GSC-registration/) for registration.
- [FIJI](https://imagej.net/Fiji) (with [TrackMate](https://imagej.net/TrackMate) installed)

### 0 Register your movie
See [this repository](https://github.com/gerhold-lab/Semi-automated-GSC-registration/) for help.

### 1 Run your movie through [TrackMate](https://imagej.net/TrackMate)
** *Script to streamline the TrackMate commands to come*

### 1 Checklist
In your data folder, you need to have the following:

|File Name| Descriptions  	|
|---	    |---	            |
|ROI.csv  | Contains x-y coordinates that was used to register the original movie  |
|u_germline.tif| The original movie, "u" for "unregistered" |
|r_germline.xml   	| The xml output from TrackMate, using the registed movie, "r" for "registered"  |

### 2 Run the script: track_pairer.py
1. If your translation matrix consists of multiple files, you need to combine them first. For example,
```
mat1 = pd.read_csv("1.csv", header = None)
mat1 = roi2mat(mat1)
mat2 = pd.read_csv("2.csv", header = None)
mat2 = roi2mat(mat2)
trans_mat = combine_roi(mat1, mat2)
```
If your translation matrix is a single csv, simply proceed to the next step.

2. If your translation matrix was obtained from a compressed movie, you need to multiply it by the number of fold. For example, if you compressed the movie by 3 fold, do
'''
trans_mat = trans_mat * 3
'''
If your translation matrix was obtained from the original movie without compression, simply proceed to the next step.

3. Crude filtering and feature generation
'''
myPairer = pairer(xml_path, trans_mat)
cells = myPairer.findNeighbors()
df = cell2df(cells)
df.to_csv ('features.csv', index = False, header=True)
X_df = pd.read_csv('features.csv', usecols = range(9))
X = X_df.to_numpy()
'''
4. Load classifier and predict
'''
X_df = pd.read_csv('features.csv', usecols = range(9))
X = X_df.to_numpy()
clf = pickle.load(open('../ML/myModel.sav', 'rb'))
# predict
y_pred = clf.predict(X)
df['Predicted_Label'] = y_pred
df.to_csv ('predictions.csv', index = False, header=True)
'''
