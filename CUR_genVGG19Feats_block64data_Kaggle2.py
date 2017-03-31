import numpy as np
import os
#import dicom
#import glob
from matplotlib import pyplot as plt
import os
import csv
import cv2
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

from keras.applications.vgg19 import VGG19
import scipy.io as sio
from scipy.misc import imresize

fileFolder = '/home/zdestefa/data/huBlockDataSetKaggleOrigSize'


origNet = VGG19(include_top=True, weights='imagenet', input_tensor=None, input_shape=None)

#net2 = Model(input=origNet.input,output=origNet.get_layer('flatten').output)
#net3 = Model(input=origNet.input,output=origNet.get_layer('fc2').output)

#Trying to model the following network
"""

def create_network():
    init = Kaiming()
    padding = dict(pad_d=1, pad_h=1, pad_w=1)
    strides = dict(str_d=2, str_h=2, str_w=2)
    dilation = dict(dil_d=2, dil_h=2, dil_w=2)
    common = dict(init=init, batch_norm=True, activation=Rectlin())
    layers = [
        Conv((9, 9, 9, 16), padding=padding, strides=strides, init=init, activation=Rectlin()),
        Conv((5, 5, 5, 32), dilation=dilation, **common),
        Conv((3, 3, 3, 64), dilation=dilation, **common),
        Pooling((2, 2, 2), padding=padding, strides=strides),
        Conv((2, 2, 2, 128), **common),
        Conv((2, 2, 2, 128), **common),
        Conv((2, 2, 2, 128), **common),
        Conv((2, 2, 2, 256), **common),
        Conv((2, 2, 2, 1024), **common),
        Conv((2, 2, 2, 4096), **common),
        Conv((2, 2, 2, 2048), **common),
        Conv((2, 2, 2, 1024), **common),
        Dropout(),
        Affine(2, init=Kaiming(local=False), batch_norm=True, activation=Softmax())
    ]
    return Model(layers=layers)

"""
input_shape = (1, 64, 64,64)
model = Sequential()
model.add(Convolution3D(16,9,9,9,border_mode='valid',input_shape=input_shape,activation='relu'))
model.add(Convolution3D(32,5,5,5,border_mode='valid',activation='relu'))
model.add(Convolution3D(64, 3, 3,3,border_mode='valid',activation='relu'))
model.add(MaxPooling3D(pool_size=(2,2,2)))
model.add(Convolution3D(128, 2, 2,2,border_mode='valid',activation='relu'))
model.add(Convolution3D(128, 2, 2,2,border_mode='valid',activation='relu'))
model.add(Convolution3D(128, 2, 2,2,border_mode='valid',activation='relu'))
model.add(Convolution3D(256, 2, 2,2,border_mode='valid',activation='relu'))
model.add(Convolution3D(1024, 2, 2,2,border_mode='valid',activation='relu'))
model.add(Convolution3D(4096, 2, 2,2,border_mode='valid',activation='relu'))
model.add(Convolution3D(2048, 2, 2,2,border_mode='valid',activation='relu'))
model.add(Convolution3D(1024, 2, 2,2,border_mode='valid',activation='relu'))
model.add(Dropout(0.2))
model.add(Flatten())
model.add(Dense(2, init='normal',activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])

def dataGenerator(filesToProcess,indRange):
    while 1:
        for ind in range(len(indRange)):
            fileP = filesToProcess[indRange[ind]]
            curMATcontent = sio.loadmat(os.path.join(fileFolder, fileP))
            huBlocks = curMATcontent["huBlocksOutput"]
            for nodInd in range(len(huBlocks)):
                currentBlock = huBlocks[nodInd, :, :, :]
                if K.image_dim_ordering() == 'th':
                    currentBlock = currentBlock.reshape(1, 1, 64, 64, 64)
                else:
                    currentBlock = currentBlock.reshape(1, 64, 64, 64, 1)
                yy = np.round(np.random.rand(1))
                YCur = int(yy[0])
                YUse = np_utils.to_categorical(YCur, 2)
                #print("Ind:" + str(ind))
                yield (currentBlock.astype('float32'),YUse)
"""
def genResNetFeatFile(fileP):
    patID = fileP[9:len(fileP) - 4]
    huBlocks= getVolData(fileP)
    rPrefix = 'resnetFeats_'
    folder4096prefix = 'data/blockFilesResizedVGG19to4096Kaggle/'
    blockNum=0
    for nodInd in range(len(huBlocks)):
        currentBlock = huBlocks[nodInd,:,:,:]
        noduleSuffix = '_Block_' + str(blockNum)
        blockNum = blockNum+1
        fileName3 = folder4096prefix + rPrefix +patID + noduleSuffix
        print("obtaining resnet data for block: " + str(blockNum))
        feats3 = getResNetData(currentBlock)
        np.save(fileName3, feats3)
"""
filesToProcess = os.listdir(fileFolder)
numFiles = len(filesToProcess)
trainRange = range(50)
validationRange = range(51,60)
model.fit_generator(dataGenerator(filesToProcess, trainRange),
                    samples_per_epoch = 1000, nb_epoch=100, nb_val_samples=50,
                    verbose=1, validation_data=dataGenerator(filesToProcess, validationRange))

