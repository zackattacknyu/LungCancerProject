import numpy as np
import csv
import time
import datetime
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution3D, MaxPooling3D, AveragePooling3D
from keras import backend as K

from keras.utils import np_utils


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

trainingRatio = 0.90
numTrainTestAll = len(trainTestIDs)
numTrain = int(np.floor(trainingRatio*numTrainTestAll))
numTest = numTrainTestAll-numTrain
numValid = len(validationIDs)

randInds = np.random.permutation(numTrainTestAll)
indsTrain = randInds[0:numTrain]
indsTest = randInds[numTrain:numTrainTestAll]

img_rows=33
img_sli=49
nb_classes=2
nb_epoch=6

fileNmPrefix1 = '/home/zdestefa/data/segFilesResizedResNetAct48/resnetFeats_'
fileNmPrefix2 = '/home/zdestefa/data/segFilesResizedResNetAct49/resnetFeats_'
img_cols1=512
img_cols2=2048
nb_filters=16
kernel_size1=(11,img_cols1,7)
kernel_size2=(11,img_cols2,7)

def getFeatureData(ids,fileNmPrefix):
    fileName = fileNmPrefix + ids + '.npy'
    dataFromFile = np.load(fileName)
    returnData = np.reshape(dataFromFile,(dataFromFile.shape[0],
                                          dataFromFile.shape[1],
                                          dataFromFile.shape[2]*dataFromFile.shape[3]))
    return returnData

def dataGenerator(patIDnumbers, patLabels, indsUse,img_cols,fileNmPrefix):
    while 1:
        for ind in range(len(indsUse)):
            patID = patIDnumbers[indsUse[ind]]
            XCur = getFeatureData(patID,fileNmPrefix)
            if K.image_dim_ordering() == 'th':
                XCur = XCur.reshape(1, 1, img_rows, img_cols, img_sli)
            else:
                XCur = XCur.reshape(1, img_rows, img_cols, img_sli, 1)
            YCur = int(patLabels[indsUse[ind]])
            YUse = np_utils.to_categorical(YCur, nb_classes)
            #print("Ind:" + str(ind))
            yield (XCur.astype('float32'),YUse)

def validDataGenerator(img_cols,fileNmPrefix):
    while 1:
        for ind in range(len(validationIDs)):
            patID = validationIDs[ind]
            XCur = getFeatureData(patID,fileNmPrefix)
            if K.image_dim_ordering() == 'th':
                XCur = XCur.reshape(1, 1, img_rows, img_cols, img_sli)
            else:
                XCur = XCur.reshape(1, img_rows, img_cols, img_sli, 1)
            yield (XCur.astype('float32'))

def getInputShape(img_cols):
    return (1, img_rows, img_cols, img_sli)


def trainAndValidateNN(img_cols,fileNmPefix,kernel_size):
    model = Sequential()

    #filter blocks to compres the info
    model.add(Convolution3D(nb_filters, kernel_size[0], kernel_size[1], kernel_size[2],
                            border_mode='valid',input_shape=getInputShape(img_cols)))
    model.add(AveragePooling3D(pool_size=(11,1,7)))

    model.add(Dropout(0.2))
    model.add(Flatten())
    model.add(Dense(128,activation='relu'))
    model.add(Dense(16,activation='sigmoid'))
    model.add(Dense(2,activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
    model.fit_generator(dataGenerator(trainTestIDs, trainTestLabels, indsTrain,img_cols,fileNmPefix),
                        samples_per_epoch=1000,nb_epoch=nb_epoch, nb_val_samples=50,verbose=1,
                        validation_data=dataGenerator(trainTestIDs, trainTestLabels,
                                                      indsTest,img_cols,fileNmPefix))

    yValidPred = model.predict_generator(validDataGenerator(img_cols,fileNmPefix),
                                         val_samples=len(validationIDs))
    pred = yValidPred[:,1]

    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d__%H_%M_%S')
    fileName = 'submissions/resNetPlusXGBoost_' + st + '.csv'

    with open(fileName, 'w') as csvfile:
        fieldnames = ['id', 'cancer']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for ind in range(len(validationIDs)):
            writer.writerow({'id': validationIDs[ind], 'cancer': str(pred[ind])})

trainAndValidateNN(img_cols2,fileNmPrefix2,kernel_size2)
trainAndValidateNN(img_cols1,fileNmPrefix1,kernel_size1)

