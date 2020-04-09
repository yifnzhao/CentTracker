# CentTracker: A trainable software for automated centrosome tracking and pairing in *C. elegans* germline

This document describes the steps to track and pair centrosomes from time-lapse movies of *C. elegans* germline.

***The batch processing pipeline tutorial is currently under development. Below we introduce the steps and development of track classification task (with a registered movie), and the detailed registration tutorial and source code can be found in [this repository](https://github.com/gerhold-lab/Semi-automated-GSC-registration/).**

## Usage (of Track Pair Classifier)

#### Materials and Requirements
- a registered time-lapse tiff movie
- [FIJI](https://imagej.net/Fiji) (with [TrackMate](https://imagej.net/TrackMate) installed)
- numpy
- pandas
- scipy
- matplotlib
- skimage
- pickle

### 0 Register your movie
See [this repository](https://github.com/gerhold-lab/Semi-automated-GSC-registration/) for help.

### 1 Run your movie through [TrackMate](https://imagej.net/TrackMate)
** *Script to streamline the TrackMate commands to come*

### 2 Checklist
In your data folder, you need to have the following:

|File Name| Descriptions  	|
|---	    |---	            |
|r_germline.tif| The registered movie, "r" for "registered" |
|r_germline.xml   	| The xml output from TrackMate, using the registed movie, "r" for "registered"  |

### 3 Run the script: track_pairer.py
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
```
trans_mat = trans_mat * 3
```
If your translation matrix was obtained from the original movie without compression, simply proceed to the next step.

3. Crude filtering and feature generation
```
myPairer = pairer(xml_path, trans_mat)
cells = myPairer.findNeighbors()
df = cell2df(cells)
df.to_csv ('features.csv', index = False, header=True)
X_df = pd.read_csv('features.csv', usecols = range(9))
X = X_df.to_numpy()
```
4. Load classifier and predict
```
X_df = pd.read_csv('features.csv', usecols = range(9))
X = X_df.to_numpy()
clf = pickle.load(open('../ML/myModel.sav', 'rb'))
# predict
y_pred = clf.predict(X)
df['Predicted_Label'] = y_pred
df.to_csv ('predictions.csv', index = False, header=True)
```

## How I built the model: a brief description of the classifier development pipeline
### 1 Data Preprocessing

##### 1. Parsing
The TrackMate output is parsed to generate the following information:
  - **edges**, consisting of
    - source spot ID
    - target spot ID
    - time
    - track ID that the edge belongs to
  - **tracks**, consisting of
    - track ID
    - t_i, the time point where the track starts
    - t_f, the time point where the track ends
    - time duration
  - **spots**, consisting of
    - x, y, z, t
    - spot ID

##### 2. Crude Filtering and Feature Generation
- For each track:
  - if track duration < 10 frames (= 5 min), discard
- For every potential track pair, the following filters are applied:
  - if the time period of overlap between the pair is less than 10 frames, discard
  - if the mean distance* between the pair is greater than 12 microns (about 50 voxels), discard

Additionally, the following statistics are calculated:

- **sl_i**: the spindle length at the track start time, i.e., the Euclidean distance between the two centrosomes at starting point;
- **sl_f**: the spindle length at the track end time, i.e., the Euclidean distance between the two centrosomes at end point;
- **sl_max**: the maximum spindle length during the cell division;
- **sl_min**: the minimum spindle length during the cell division;
- **t_cong**: the number of continuous time points in which the spindle length is under 4 microns (15 voxels);
- **t_overlap**: track duration;
- **center_stdev**: the standard deviation of the cell center position, by taking the square root of the sum of the variances of x, y, z coordinates of the center point (i.e., the midpoint of the two centrosome locations) over the track duration;
- **normal_stdev**: the standard deviation of the normal vector of the metaphase plate, i.e., stdev of the direction vector obtained by (x1,y1,z1) - (x2,y2,z2) for all time points, where (x1,y1,z1) and (x2,y2,z2) are centrosome locations of the track pair at a given time point.
- **dist_center_to_border**: the Euclidean distance from the mean cell center point to the closest movie border (the border before registration). This feature is designed to discriminate the spurious tracks on the borders likely due to the movie registration.

*Note: **mean distance** is calculated by taking the average of the spindle length at each time point. It is not included as a classification feature.

##### 3. Building a classifier
###### 1) Model selection
The following classifiers are selected for testing:
  - [AdaBoost](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.AdaBoostClassifier.html)
  - [Random Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html)
  - [Decision Tree](https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html)
  - [Linear Support Vector Machine](https://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVC.html#sklearn.svm.LinearSVC)
  - [SVM with Stochastic Gradient Descent](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.SGDClassifier.html#sklearn.linear_model.SGDClassifier)
  - [Logistic Regression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html)

###### 2) Data Preprocessing
  - Data: The current dataset consists of three 3D time-lapse microscopy movies of *C. elegans* taken under similar imaging conditions (courtesy of Réda Zellag) and corresponding trackmate output and manual labels. The trackmate output are first processed and features are generated as described in the sections above, Parsing, and Crude Filtering and Feature Generation.
  - Train-Test Split: the dataset is shuffled and split into training set (67%) and testing set (33%)

###### 3) Hyperparameter tuning
1. Selecting hyperparameter range with stratified cross validation
  Results: see [fig](https://github.com/yifnzhao/semi-automated-centrosome-pairing/blob/master/fig/)
2. Random search to tune hyperparameter with bootstraping
  Results: RandomForestClassifier with the following hyperparameters gives the best precision score (positive predictive value) during the validation phase.
  ```
  rf_clf = RandomForestClassifier(min_impurity_decrease=4.496833213815348e-07,criterion='gini',warm_start=True, n_estimators=10)
  ```

  ###### 4) Predict and Test
  - precision score: 0.9698620804253906
  - accuracy score: 0.9694915254237289
  - classification report:

|     | precision    | recall    |f1-score|support|
  | ------------- |------------- | ------------- | ------------- | ------------- |
  | 0      | 0.98        | 0.98       | 0.98   | 256|
  | 1      | 0.88     | 0.90     | 0.89   | 39|
  |accuracy|||0.97|295|
  |macro avg   | 0.93 |     0.94 |    0.93  |    295|
  |  weighted avg |0.97  |    0.97|      0.97 |      295|
