import numpy as np
import math

def loadFreq():
    # load vocabulary and assign index
    vocmap = dict()
    f = open('freqwords', 'r')
    c = 0
    for line in f:
        vocmap[line.rstrip()] = c
        c += 1
    vocmap['UNKA'] = c
    f.close()
    #print 'Vocabulary size:', len(vocmap)
    return vocmap

def loadTrainData(vocmap):
    # load the training corpus
    # load sentence and label
    f = open('train.txt', 'r')
    wordList = []
    labelList = []
    for line in f:
        data = line.strip().split()
        tmp = data[0::2]
        wordList.append([vocmap[s] if s in vocmap else vocmap['UNKA'] for s in tmp])
        tmp = data[1::2]
        labelList.append(tmp)
    f.close()
    return wordList, labelList

def loadTag(labelList):
    # construct tagset and assign index
    tagmap = dict()
    for sent in labelList:
        for i in range(len(sent)):
            if not sent[i] in tagmap:
                tagmap[sent[i]] = len(tagmap)
            sent[i] = tagmap[sent[i]]
    #print 'Tagset size:', len(tagmap)

    return tagmap

def splitDataAndGetCounts(ratio, wordList, labelList, vocmap, tagmap):
    #split the fully labeled data by the ratio and return the count and all sentences

    # split data
    labelNum = int(ratio * len(wordList))
    unlabelWordList = wordList[labelNum:]
    unlabelLabelList = labelList[labelNum:]
    wordList = wordList[:labelNum]
    labelList = labelList[:labelNum]

    # construct parameter table
    W = len(vocmap)
    T = len(tagmap)

    t = np.zeros(T)
    tw = np.zeros((T, W))
    tpw = np.zeros((T, W))
    tnw = np.zeros((T, W))

    # calculate count to the table
    for i in range(len(wordList)):
        word = wordList[i]
        label = labelList[i]
        for j in range(len(word)):
            t[label[j]] += 1.0
            tw[label[j], word[j]] += 1.0
            if j > 0:
                tpw[label[j], word[j-1]] += 1.0
            if j < len(word) - 1:
                tnw[label[j], word[j+1]] += 1.0

    # smoothing
    smoothing(1.0, t, tw, tpw, tnw)

    return t, tw, tpw, tnw, unlabelWordList, unlabelLabelList

def smoothing(alpha, t, tw, tpw, tnw):
    # adding the smooth counts to the original ones
    T, W = tw.shape
    t += alpha / T
    tw += alpha / (T * W)
    tpw += alpha / (T * W)
    tnw += alpha / (T * W)


def Mstep(et, etw, etpw, etnw, t, tw, tpw, tnw):
    # ratio: the split ratio of labeled and unlabled data; used to compute weight of real counts
    T, W = etw.shape
    pt = np.zeros(et.shape)
    ptw = np.zeros(etw.shape)
    ptpw = np.zeros(etpw.shape)
    ptnw = np.zeros(etnw.shape)

    # c is the weight of real count
    c = 100.0

    # Estimate parameters pt, ptw, ptpw, ptnw based on the expected counts and real counts
    pt = c * t + et
    pt /= pt.sum(axis=0)
    ptw = c * tw + etw
    ptw /= ptw.sum(axis=1)[:, np.newaxis]
    ptpw = c * tpw + etpw
    ptpw /= ptpw.sum(axis=1)[:, np.newaxis]
    ptnw = c * tnw + etnw
    ptnw /= ptnw.sum(axis=1)[:, np.newaxis]

    return pt, ptw, ptpw, ptnw

def accuracy_cal(labelList, pred, i):
    accres = sum([1 if labelList[i][j] == pred[i][j] else 0 for j in range(len(labelList[i]))])
    return accres

def loadTestData(vocmap, tagmap):
    # load and return the test data and gold label, converted into index

    wordList = []
    labelList = []

    f = open('test.txt', 'r')
    for line in f:
        data = line.strip().split()
        tmp = data[0::2]
        wordList.append([vocmap[s] if s in vocmap else vocmap['UNKA'] for s in tmp])
        tmp = data[1::2]
        labelList.append([tagmap[s] for s in tmp])
    f.close()

    return wordList, labelList
    
def predictA(wordList, pt, ptw, ptpw, ptnw):
    pred = []

    # Predict tag index in each sentence based on Model A
    for sent in wordList:
        cur_pred = []
        for pos in xrange(len(sent)):
            # pred_tag is the prediction of tag for the current word
            pred_tag = -1
                        
            p = pt * ptw[:,sent[pos]]
            pred_tag = np.argmax(p)

            # append the prediction to the list
            cur_pred.append(pred_tag)
        pred.append(cur_pred)

    return pred


def predictB(wordList, pt, ptw, ptpw, ptnw):
    pred = []
    # Predict tag index in each sentence based on Model B
    for sent in wordList:
        cur_pred = []
        for pos in xrange(len(sent)):
            # pred_tag is the prediction of tag for the current word
            pred_tag = -1
                        
            p = pt * ptw[:,sent[pos]]
            if pos > 0:
                p *= ptpw[:,sent[pos-1]]
            pred_tag = np.argmax(p)

            # append the prediction to the list
            cur_pred.append(pred_tag)
        pred.append(cur_pred)

    return pred

def evaluate(labelList, pred):
    # compute accuracy
    acc = 0.0
    total = 0.0
    for i in range(len(labelList)):
        total += len(labelList[i])
        acc += accuracy_cal(labelList, pred, i)
    return acc / total

def output_write(data1, data2):
    fileacc = open("result.txt", "a")
    fileacc.write(str(data1)+'\n')
    fileacc.write(str(data2)+'\n')

resvocmap = loadFreq()
Train_wordList, Train_labelList = loadTrainData(resvocmap)
Train_tagmap = loadTag(Train_labelList)
Train_t, Train_tw, Train_tpw, Train_tnw, Train_unlabelWordList, Train_unlabelLabelList = splitDataAndGetCounts(1.0, Train_wordList, Train_labelList, resvocmap, Train_tagmap)
# estimate the parameters
Train_pt, Train_ptw, Train_ptpw, Train_ptnw = Mstep(np.zeros(Train_t.shape), np.zeros(Train_tw.shape), np.zeros(Train_tpw.shape), np.zeros(Train_tnw.shape), Train_t, Train_tw, Train_tpw, Train_tnw)

Test_wordList, Test_labelList = loadTestData(resvocmap, Train_tagmap)
respredA = predictA(Test_wordList, Train_pt, Train_ptw, Train_ptpw, Train_ptnw)
accuracyA = evaluate(Test_labelList, respredA)
respredB = predictB(Test_wordList, Train_pt, Train_ptw, Train_ptpw, Train_ptnw)
accuracyB = evaluate(Test_labelList, respredB)

output_write(accuracyA, accuracyB)