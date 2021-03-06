import numpy as np
#import dicom
#import glob
from matplotlib import pyplot as plt
import os
import csv
#import cv2
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
"""
def get_extractor():
    model = mx.model.FeedForward.load('model/resnet-50', 0, ctx=mx.cpu(), numpy_batch_size=1)
    fea_symbol = model.symbol.get_internals()["flatten0_output"]
    feature_extractor = mx.model.FeedForward(ctx=mx.cpu(), symbol=fea_symbol, numpy_batch_size=64,
                                             arg_params=model.arg_params, aux_params=model.aux_params,
                                             allow_extra_params=True)

    return feature_extractor


def get_3d_data(path):
    slices = [dicom.read_file(path + '/' + s) for s in os.listdir(path)]
    slices.sort(key=lambda x: int(x.InstanceNumber))
    return np.stack([s.pixel_array for s in slices])


def get_data_id(path):
    sample_image = get_3d_data(path)
    sample_image[sample_image == -2000] = 0
    # f, plots = plt.subplots(4, 5, sharex='col', sharey='row', figsize=(10, 8))

    batch = []
    cnt = 0
    dx = 40
    ds = 512
    for i in range(0, sample_image.shape[0] - 3, 3):
        tmp = []
        for j in range(3):
            img = sample_image[i + j]
            img = 255.0 / np.amax(img) * img
            img = cv2.equalizeHist(img.astype(np.uint8))
            img = img[dx: ds - dx, dx: ds - dx]
            img = cv2.resize(img, (224, 224))
            tmp.append(img)

        tmp = np.array(tmp)
        batch.append(np.array(tmp))

        # if cnt < 20:
        #     plots[cnt // 5, cnt % 5].axis('off')
        #     plots[cnt // 5, cnt % 5].imshow(np.swapaxes(tmp, 0, 2))
        # cnt += 1

    # plt.show()
    batch = np.array(batch)
    return batch


def calc_features():
    net = get_extractor()
    for folder in glob.glob('stage1/*'):
        batch = get_data_id(folder)
        feats = net.predict(batch)
        print(feats.shape)
        np.save(folder, feats)
"""

# if K.image_dim_ordering() == 'th':
#     input_shape = (1, img_rows, img_cols,img_sli)
# else:
#     input_shape = (img_rows, img_cols,img_sli, 1)

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

def getVolData(patID):
    patFile = "/home/zdestefa/data/segFilesResizedAll/resizedSegDCM_" + patID + ".mat"
    curMATcontent = sio.loadmat(patFile)
    volData = curMATcontent["resizedDCM"]
    return volData.astype('float32')

origNet = ResNet50(include_top=True, weights='imagenet', input_tensor=None, input_shape=None)
net = Model(input=origNet.input,output=origNet.get_layer('flatten_1').output)

#Here is output showing that the Activation_49 layer has 2048x7x7 nodes and the 2D one
#   We will want to use

#>>> myLayer = origNet.get_layer('activation_49')
#>>> myLayer.output_shape
#(None, 2048, 7, 7)


def genResNetFeatFile(id):
    fileName = 'data/segFilesResizedResNet/resnetFeats_' + id + '.npy'
    curData = getVolData(id)
    curDataReshape = np.reshape(curData,(1,256,256,100))
    batch = []
    cnt = 0
    dx = 40
    ds = 512
    for i in range(0, curData.shape[2] - 3, 3):
        tmp = []
        for j in range(3):
            img2 = curData[i + j]
            img = imresize(img2,(224,224))
            tmp.append(img)
        tmp = np.array(tmp)
        batch.append(np.array(tmp))
    batch = np.array(batch)
    feats = net.predict(batch)
    print('current resnet output shape:')
    print(feats.shape)
    np.save(fileName, feats)

def calc_featuresA():
    for id in trainTestIDs:
        genResNetFeatFile(id)
    for id in validationIDs:
        genResNetFeatFile(id)



def train_xgboost():
    #df = pd.read_csv('data/stage1_labels.csv')
    #print(df.head())

    #x = np.array([np.mean(np.load('stage1/%s.npy' % str(id)), axis=0) for id in df['id'].tolist()])

    print('Train/Validation Data Shape:')
    #x = np.array([np.mean(getVolData(id), axis=0) for id in trainTestIDs.tolist()])
    x = np.array([np.mean(getVolData(id), axis=0) for id in trainTestIDs])
    print(x.shape)
    y = trainTestLabels.as_matrix()

    # trn_x, val_x, trn_y, val_y = cross_validation.train_test_split(x, y, random_state=42, stratify=y,
    #                                                                test_size=0.20)
    #
    # clf = xgb.XGBRegressor(max_depth=10,
    #                        n_estimators=1500,
    #                        min_child_weight=9,
    #                        learning_rate=0.05,
    #                        nthread=8,
    #                        subsample=0.80,
    #                        colsample_bytree=0.80,
    #                        seed=4242)
    #
    # clf.fit(trn_x, trn_y, eval_set=[(val_x, val_y)], verbose=True, eval_metric='logloss', early_stopping_rounds=50)
    # return clf


def make_submit():
    #clf = train_xgboost()
    train_xgboost()
    #df = pd.read_csv('data/stage1_sample_submission.csv')

    #x = np.array([np.mean(getVolData(id), axis=0) for id in validationIDs.tolist()])
    x = np.array([np.mean(getVolData(id), axis=0) for id in validationIDs])
    print('Test Data Shape:')
    print(x.shape)
    #pred = clf.predict(x)

    # df['cancer'] = pred
    # df.to_csv('subm1.csv', index=False)
    # print(df.head())


if __name__ == '__main__':
    calc_featuresA()
    #make_submit()