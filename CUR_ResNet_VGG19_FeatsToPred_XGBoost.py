import numpy as np
#import dicom
#import glob
from matplotlib import pyplot as plt
import os
import csv
#import cv2
import time
import datetime
# import mxnet as mx
# import pandas as pd
# from sklearn import cross_validation
# import xgboost as xgb
from keras.datasets import mnist
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, MaxPooling2D
from keras.layers import Convolution3D, MaxPooling3D
from keras.utils import np_utils
from keras import backend as K

from keras.applications.resnet50 import ResNet50
import scipy.io as sio
from scipy.misc import imresize
from sklearn import cross_validation
import xgboost as xgb
from keras.utils import np_utils
import glob

trainTestIDs = []
trainTestLabels = []
validationIDs = []
with open('stage1_labels.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        trainTestIDs.append(row['id'])
        trainTestLabels.append(row['cancer'])

with open('stage1_sample_submission.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        validationIDs.append(row['id'])

numGivenFeat1=4096
numGivenFeat2=2048
numTotalFeats1 = numGivenFeat1*1
numConcatFeats = numGivenFeat2*1 + numGivenFeat1*1

def getFeatureData(id):
    outVec = np.zeros((1, numConcatFeats))

    fileName1 = '/home/zdestefa/data/segFilesResizedVGG19to4096/resnetFeats_' + id + '.npy'
    featData1 = np.load(fileName1)
    outVec[0, 0:numGivenFeat1] = np.mean(featData1, axis=0)
    #outVec[0, numGivenFeat1:numGivenFeat1 * 2] = np.max(featData1, axis=0)  # this causes potential overfit. should remove
    #outVec[0, numGivenFeat1 * 2:numGivenFeat1 * 3] = np.min(featData1, axis=0)  # this causes potential overfit. should remove

    fileName2 = '/home/zdestefa/data/segFilesResizedResNet/resnetFeats_' + id + '.npy'
    featData2 = np.load(fileName2)
    outVec[0, numTotalFeats1:numTotalFeats1+numGivenFeat2] = np.mean(featData2, axis=0)
    #outVec[0, numTotalFeats1+numGivenFeat2:numTotalFeats1+numGivenFeat2*2] = np.max(featData2, axis=0)  # this causes potential overfit. should remove
    # outVec[0, numGivenFeat * 2:numGivenFeat * 3] = np.min(featData, axis=0)  # this causes potential overfit. should remove
    return outVec

# for fileNm in glob.glob('/home/zdestefa/data/segFilesResizedResNet/*.npy'):
#     curData = np.load(fileNm)
#     print('Name: ' + fileNm)
#     print('Shape:' + str(curData.shape))

def train_xgboost():
    #df = pd.read_csv('data/stage1_labels.csv')
    #print(df.head())

    #x = np.array([np.mean(np.load('stage1/%s.npy' % str(id)), axis=0) for id in df['id'].tolist()])

    print('Train/Validation Data being obtained')
    #x = np.array([np.mean(getVolData(id), axis=0) for id in trainTestIDs.tolist()])

    x = np.zeros((len(trainTestIDs),numConcatFeats))
    ind = 0
    for id in trainTestIDs:
        x[ind,:] = getFeatureData(id)
        ind = ind+1
        #x.append(np.array([np.mean(featData,axis=0)]))
    print('Finished getting train/test data')
    #y = np_utils.to_categorical(trainTestLabels, 2)
    y = [float(lab) for lab in trainTestLabels]
    trn_x, val_x, trn_y, val_y = cross_validation.train_test_split(x, y, random_state=42, stratify=y,
                                                                   test_size=0.20)

    clf = xgb.XGBRegressor(max_depth=30,
                           n_estimators=1500,
                           min_child_weight=9,
                           learning_rate=0.05,
                           nthread=8,
                           subsample=0.80,
                           colsample_bytree=0.80,
                           seed=4242)

    clf.fit(trn_x, trn_y, eval_set=[(val_x, val_y)], verbose=True,
            eval_metric='logloss', early_stopping_rounds=100)
    return clf


def make_submit():
    clf = train_xgboost()

    print('Kaggle Test Data being obtained')
    x2 = np.zeros((len(validationIDs), numConcatFeats))
    ind = 0
    for id in validationIDs:
        x2[ind, :] = getFeatureData(id)
        ind = ind + 1
    print('Finished getting kaggle test data')

    pred = clf.predict(x2)

    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d__%H_%M_%S')
    fileName = 'submissions/VGG19ResNetPlusXGBoost_' + st + '.csv'

    with open(fileName, 'w') as csvfile:
        fieldnames = ['id', 'cancer']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for ind in range(len(validationIDs)):
            writer.writerow({'id': validationIDs[ind], 'cancer': str(pred[ind])})

    # df['cancer'] = pred
    # df.to_csv('subm1.csv', index=False)
    # print(df.head())


if __name__ == '__main__':
    #calc_featuresA()
    make_submit()