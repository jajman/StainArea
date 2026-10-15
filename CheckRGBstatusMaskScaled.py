from matplotlib import pyplot as plt
from matplotlib import image as mpimg
from PIL import Image, ImageDraw, ImageFont
import time, os

def getFileName(fileName):
    lenFIleName = len(fileName)
    nameEnd = 0
    nameStart = 0
    isDot=False
    for i in reversed(range(lenFIleName)):
        if fileName[i] == '.':
            if isDot:
                continue
            else:
                nameEnd = i
                isDot=True
        if fileName[i] == '/':
            nameStart = i + 1
            break
    return fileName[nameStart:nameEnd]

def getFileExt(fileName):
    lenFIleName = len(fileName)
    nameEnd = 0
    nameStart = 0
    isDot=False
    for i in reversed(range(lenFIleName)):
        if fileName[i] == '.':
            return fileName[i+1:]

################################################
baseName="hCS 37d HSY A2-14 A7-6 37d BrdU"

orgImageDir=baseName+"_org/"
maskImageDir=baseName+"_m2/"
destImageDir=baseName+"_txt_scaled/"

if not os.path.exists(destImageDir):
    os.makedirs(destImageDir)


RedThreshold=50
GreenThreshold=50
BlueThreshold=50
################################################

scaleBarLengthFile=baseName+"_scale_length.txt"
scaleBarValueFile=baseName+"_scale.txt"

with open(scaleBarLengthFile,
          'rt') as f:
    scaleBarLength=f.readlines()
scaleBarLengthList=[]
firstLine=0
for lineTxt in scaleBarLength:
    firstLine+=1
    if firstLine>1:
        newTxt=lineTxt.strip().split("\t")
        scaleBarLengthList.append(newTxt)

with open(scaleBarValueFile,
          'rt') as f:
    scaleBarValue=f.readlines()
scaleBarValueList=[]
firstLine=0
for lineTxt in scaleBarValue:
    firstLine+=1
    if firstLine>1:
        newTxt=lineTxt.strip().split("\t")
        scaleBarValueList.append(newTxt)

if len(scaleBarLengthList)!=len(scaleBarValueList):
    print("Different length")

fileAreaDict={}
for index1 in range(len(scaleBarLengthList)):
    if scaleBarLengthList[index1][0]!=scaleBarValueList[index1][0]:
        print("Different file Name")
    if scaleBarLengthList[index1][0] == scaleBarValueList[index1][0]:
        scaleLen=int(scaleBarLengthList[index1][1])
        scaleVal = int(scaleBarValueList[index1][1])
        ratio=scaleVal/scaleLen
        area=ratio*ratio
        print(area)
        fileAreaDict[scaleBarLengthList[index1][0]]=area


maskFiles=os.listdir(orgImageDir)
fileNum=0
allFileNum=len(maskFiles)


for imageFile in maskFiles:
    fileNum+=1
    print(str(fileNum)+'/'+str(allFileNum))

    startTime = time.time()

    fileName = getFileName(imageFile)
    catIm = Image.open(orgImageDir+imageFile)
    catImM = Image.open(maskImageDir+fileName + '-m.' + getFileExt(imageFile))
    (x, y) = catIm.size

    allImgSize = x * y

    numR = 0
    numG = 0
    numB = 0
    numRG = 0
    numRB = 0
    numGB = 0
    numRGB = 0

    totalR = 0
    totalG=0
    totalB=0

    totalTR=0
    totalTG = 0
    totalTB = 0


    maskPixel = 0
    txtToWrite=''
    for i in range(x):
        if i % 500 == 0:
            print(i)
        for j in range(y):
            colorXYMask = catImM.getpixel((i, j))
            if colorXYMask[0] > 200 and colorXYMask[1] > 200 and colorXYMask[2] > 200:
                maskPixel += 1
                colorXY = catIm.getpixel((i, j))
                totalR += colorXY[0]
                totalG += colorXY[1]
                totalB += colorXY[2]
                if colorXY[0] > RedThreshold:
                    numR += 1
                    totalTR+=colorXY[0]
                if colorXY[1] > GreenThreshold:
                    numG += 1
                    totalTG += colorXY[1]
                if colorXY[2] > BlueThreshold:
                    numB += 1
                    totalTB += colorXY[2]
                if colorXY[0] > RedThreshold and colorXY[1] > GreenThreshold:
                    numRG += 1
                if colorXY[0] > RedThreshold and colorXY[2] > BlueThreshold:
                    numRB += 1
                if colorXY[1] > GreenThreshold and colorXY[2] > BlueThreshold:
                    numGB += 1
                if colorXY[0] > RedThreshold and colorXY[1] > GreenThreshold and colorXY[2] > BlueThreshold:
                    numRGB += 1

    avgR=int(totalR/maskPixel)
    avgG = int(totalG / maskPixel)
    avgB = int(totalB / maskPixel)
    if numR>0:
        avgTR = int(totalTR / numR)
    else:
        avgTR = 0
    if numG > 0:
        avgTG = int(totalTG / numG)
    else:
        avgTG = 0
    if numB > 0:
        avgTB = int(totalTB / numB)
    else:
        avgTB = 0
    areaVal=fileAreaDict[fileName]
    txtToWrite = 'RedThreshold:\t' + str(RedThreshold) + '\n'
    txtToWrite += 'GreenThreshold:\t' + str(GreenThreshold) + '\n'
    txtToWrite += 'BlueThreshold:\t' + str(BlueThreshold) + '\n'
    txtToWrite += 'Total area:\t' + str(x * y*areaVal) + '\n'
    txtToWrite += 'Total mask area:\t' + str(maskPixel*areaVal) + '\n'
    txtToWrite += 'Red area:\t' + str(numR*areaVal) + '\n'
    txtToWrite += 'Green area:\t' + str(numG*areaVal) + '\n'
    txtToWrite += 'Blue area:\t' + str(numB*areaVal) + '\n'
    txtToWrite += 'Red and Green area:\t' + str(numRG*areaVal) + '\n'
    txtToWrite += 'Red and Blue area:\t' + str(numRB*areaVal) + '\n'
    txtToWrite += 'Green and Blue area:\t' + str(numGB*areaVal) + '\n'
    txtToWrite += 'Red and Green and Blue area:\t' + str(numRGB*areaVal) + '\n'
    txtToWrite += 'Red avg over T:\t' + str(avgTR) + '\n'
    txtToWrite += 'Green avg over T:\t' + str(avgTG) + '\n'
    txtToWrite += 'Blue avg over T:\t' + str(avgTB) + '\n'
    txtToWrite += 'Red avg:\t' + str(avgR) + '\n'
    txtToWrite += 'Green avg:\t' + str(avgG) + '\n'
    txtToWrite += 'Blue avg:\t' + str(avgB) + '\n'


    with open(destImageDir+fileName + '-' + str(RedThreshold) + '-' + str(GreenThreshold) + '-' + str(BlueThreshold) + '.txt',
              'wt') as f:
        f.write(txtToWrite)

    endTime = time.time()

    print(str(endTime - startTime))


#os.system("shutdown /s /t 0")