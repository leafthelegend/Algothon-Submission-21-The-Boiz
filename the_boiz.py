import numpy as np
nInst=100
currentPos = np.zeros(nInst)
tradedPrices = np.zeros(nInst)
watchingUp, watchingDown = [False]*nInst, [False]*nInst
sells = [[] for i in range(nInst)]
shorts = [[] for i in range(nInst)]
buys = [[] for i in range(nInst)]
shortCloses = [[] for i in range(nInst)]

shortsPaused = [False]*nInst
buysPaused = [False]*nInst

def getMyPosition (prcSoFar):
    global currentPos
    global watchingUp
    global watchingDown
    global shortsPaused
    global buysPaused
    (nins,nt) = prcSoFar.shape
    for i in range(nins):
        prcData = prcSoFar[i]
        sum = 0
        windowSize = 4

        avg = movingAverage(prcData,windowSize)
        currentAvg = avg[-1]
        threshold, jumpThreshold, bailThreshold = get_threshold(prcData,avg,windowSize)
        prcNow = prcData[-1]
        bidSize = 10000/prcNow

        if (prcNow>currentAvg and prcData[-2]<currentAvg) or (prcNow<currentAvg and prcData[-2]>currentAvg):
            shortsPaused[i] = False
            buysPaused[i] = False
        if shortsPaused[i] and (prcNow-currentAvg) > 3*threshold:
            shortsPaused[i] = False
        if buysPaused[i] and (prcNow-currentAvg) < -3*threshold:
            buysPaused[i] = False

        if (prcNow-currentAvg) > threshold and not shortsPaused[i]:
            if currentPos[i] >= 0:
                shorts[i].append(len(prcData))
                currentPos[i] = -bidSize
                tradedPrices[i] = prcNow
                watchingDown[i] = False
        if (prcNow-currentAvg) < -threshold and not buysPaused[i]:
            if currentPos[i] <= 0:
                buys[i].append(len(prcData))
                currentPos[i] = bidSize
                tradedPrices[i] = prcNow
                watchingUp[i] = False

        if currentPos[i]<0 and prcNow < currentAvg:
            if prcNow - currentAvg < -jumpThreshold:
                watchingUp[i] = True
            else:
                currentPos[i]=0
                shortCloses[i].append(len(prcData))
        if currentPos[i]>0 and prcNow > currentAvg:
            if prcNow - currentAvg > jumpThreshold:
                watchingDown[i] = True
            else:
                currentPos[i]=0
                sells[i].append(len(prcData))

        if currentPos[i]<0 and prcNow > tradedPrices[i]+bailThreshold:
            print('yeet')
            currentPos[i]=0
            shortCloses[i].append(len(prcData))
            shortsPaused[i] = True
            watchingUp[i] = False
            watchingDown[i] = False
        if currentPos[i]>0 and prcNow < tradedPrices[i]-bailThreshold:
            print('yote')
            currentPos[i]=0
            sells[i].append(len(prcData))
            buysPaused[i] = True
            watchingUp[i] = False
            watchingDown[i] = False

        if watchingUp[i] and (prcNow > currentAvg or (prcNow-currentAvg) < -threshold):
            if currentPos[i] != 0:
                shortCloses[i].append(len(prcData))
            currentPos[i] = 0
            watchingUp[i] = False
        if watchingDown[i] and (prcNow < currentAvg or (prcNow-currentAvg) > threshold) :
            if currentPos[i] != 0:
                sells[i].append(len(prcData))
            currentPos[i] = 0
            watchingDown[i] = False
        latestJump = prcNow - prcData[-2]
        if watchingUp[i] and latestJump > jumpThreshold:
            if currentPos[i] != 0:
                shortCloses[i].append(len(prcData))
            currentPos[i] = 0
            watchingUp[i] = False
        if watchingDown[i] and latestJump < -jumpThreshold:
            if currentPos[i] != 0:
                sells[i].append(len(prcData))
            currentPos[i] = 0
            watchingDown[i] = False

    currentPos = [int(i) for i in currentPos]
    return(currentPos)

def get_threshold(prcData,avg,windowSize):
    windowSize = min(windowSize,len(prcData)//2)
    windowSize = max(windowSize,len(prcData)-len(avg))
    deviation = [abs(prcData[i]-avg[i-windowSize]) for i in range(windowSize,len(prcData))]
    threshold = sorted(deviation)[int(len(deviation)*0.7)]
    bailThreshold = threshold
    percentThreshold = (threshold/prcData[-1])
    if percentThreshold < 0.035:
        threshold = 0.035*prcData[-1]
    jumps = [abs(prcData[i+1]-prcData[i]) for i in range(len(prcData)-1)]
    jumps = [i for i in jumps if i != 0]
    jumpThreshold = sorted(jumps)[int(len(jumps)*0.9)]
    return(threshold,jumpThreshold,bailThreshold)

def movingAverage(prcData, windowSize):
    averages = []
    for i in range(len(prcData)-windowSize):
        sum = 0
        for k in range(windowSize):
            sum += prcData[i+k]
        avg = sum/windowSize
        averages.append(avg)
    return(averages)

def mean(arr):
    sum = 0
    for i in arr:
        sum+=i
    sum/=len(arr)
    return(sum)
