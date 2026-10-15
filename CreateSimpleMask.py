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


################################################
baseName='hCS 37d HSY A2-14 A7-6 37d BrdU'
orgImageDir=baseName+"_org/"
destImageDir=baseName+"_m/"
os.makedirs(destImageDir, exist_ok=True)
################################################


maskFiles=os.listdir(orgImageDir)
fileNum=0
allFileNum=len(maskFiles)
for file in maskFiles:
    fileNum+=1
    print(str(fileNum)+'/'+str(allFileNum))
    fileName = getFileName(file)

    startTime = time.time()

    catIm = Image.open(orgImageDir+file)
    (x, y) = catIm.size
    print(str(x) + ' ' + str(y))
    imM = Image.new('RGB', (x, y), 'black')


    allPixel = 0
    targetPixel = 0
    for i in range(x):
        if i % 500 == 0:
            print(i)
        for j in range(y):
            #allPixel += 1
            if i>(x-450) and j>(y-60):
                continue
            colorXY = catIm.getpixel((i, j))
            totStrength=colorXY[0]+colorXY[1]+colorXY[2]
            if totStrength>55 and totStrength<750:
                imM.putpixel((i, j), (255,255,255))


    imM.save(destImageDir+fileName + '-m.jpg')


    endTime = time.time()

    print(str(endTime - startTime))
