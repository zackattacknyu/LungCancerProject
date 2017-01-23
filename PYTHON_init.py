'''Trains a simple convnet on the MNIST dataset.

Gets to 99.25% test accuracy after 12 epochs
(there is still a lot of margin for parameter tuning).
16 seconds per epoch on a GRID K520 GPU.
'''

from __future__ import print_function
import numpy as np
import os
np.random.seed(1337)  # for reproducibility

from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, MaxPooling2D
from keras.utils import np_utils
from keras import backend as K

import scipy.io as sio
from sklearn.cross_validation import train_test_split

batch_size = 128
nb_classes = 10
nb_epoch = 12

# input image dimensions
img_rows, img_cols = 28, 28
# number of convolutional filters to use
nb_filters = 32
# size of pooling area for max pooling
pool_size = (2, 2)
# convolution kernel size
kernel_size = (3, 3)

# the data, shuffled and split between train and test sets
#(X_train, y_train), (X_test, y_test) = mnist.load_data()

#print(X_train.shape)

matFiles = []

trainTestInfo = sio.loadmat("stage1_labelsMAT.mat")
trainTestIDs = trainTestInfo["names"]
trainTestLabels = trainTestInfo["labelData"]

trainIDs,testIDs,trainLabels,testLabels = train_test_split(trainTestIDs,trainTestLabels,test_size=0.2,random_state=42)

print(trainIDs.shape)
print(testIDs.shape)
print(trainLabels.shape)
print(testLabels.shape)

for root, dirs, files in os.walk("/home/zdestefa/data/segFilesResizedAll"):
    for file in files:
        if file.endswith(".mat"):
            curFile = os.path.join(root, file)
            #curMATcontents = sio.loadmat(curFile)
            #matFiles.append(curMATcontents)
            #print(curFile)
