from matplotlib import pyplot as plt
from matplotlib import image as mpimg
from PIL import Image, ImageDraw, ImageFont
import time, os
import cv2
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = (
    r'C:\Program Files\Tesseract-OCR\tesseract.exe'
)

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

def read_scale_number(image_path, p1, p2, debug_path=None):
    """
    지정한 좌표 영역을 crop해서 OCR로 숫자만 읽어 반환

    Parameters
    ----------
    image_path : str
        이미지 파일 경로

    p1 : tuple
        (x1, y1)

    p2 : tuple
        (x2, y2)

    debug_path : str or None
        crop/OCR 이미지를 저장하고 싶으면 경로 지정
        예: 'debug.jpg'

    Returns
    -------
    int or None
        인식된 숫자
        실패하면 None
    """

    img = cv2.imread(image_path)

    if img is None:
        print("Image read failed:", image_path)
        return None

    x1, y1 = p1
    x2, y2 = p2

    # crop
    crop = img[y1:y2, x1:x2]

    if crop.size == 0:
        print("Invalid crop area")
        return None

    # grayscale
    gray = cv2.cvtColor(
        crop,
        cv2.COLOR_BGR2GRAY
    )

    # 작은 글씨이므로 확대
    gray = cv2.resize(
        gray,
        None,
        fx=5,
        fy=5,
        interpolation=cv2.INTER_CUBIC
    )

    # 흰 글씨 강조
    _, binary = cv2.threshold(
        gray,
        120,
        255,
        cv2.THRESH_BINARY
    )

    # debug image 저장
    if debug_path is not None:
        cv2.imwrite(
            debug_path,
            binary
        )

    # 숫자만 OCR
    config = (
        '--psm 7 '
        '-c tessedit_char_whitelist=0123456789'
    )

    text = pytesseract.image_to_string(
        binary,
        config=config
    )



    # 숫자만 추출
    match = re.search(
        r'\d+',
        text
    )

    if match:
        return int(
            match.group()
        )

    return None

################################################
baseName='hCS 37d HSY A2-14 A7-6 37d BrdU'
orgImageDir=baseName+"_org/"

################################################

txtToWriteScaleLength=('FileName'+'\t'+'scale'+'\n')
txtToWriteScale=('FileName'+'\t'+'scale'+'\n')

maskFiles=os.listdir(orgImageDir)
fileNum=0
allFileNum=len(maskFiles)

for fileTo in maskFiles:
    fileNum+=1
    print(str(fileNum) + '/' + str(allFileNum))

    fileName = getFileName(fileTo)
    startTime = time.time()

    catIm = Image.open(orgImageDir + fileTo)
    (x, y) = catIm.size
    print(str(x) + ' ' + str(y))

    startNum = 0
    startScale = 0
    endNum = 0
    endScale = 0
    numWhite = 0
    posYdelta = 0

    for i in range(1200):
        color40=[]
        for j in range(60):
            colorXY = catIm.getpixel((x-1-i, y-1-j))
            color40.append(colorXY)
        numWhite = 0
        for k in range(60):
            if color40[k][0]>200 and color40[k][1]>200 and color40[k][2]>200:
                numWhite+=1
            if numWhite==3:
                posYdelta=k-5

        if numWhite>2 and startScale==0:
            startNum=(x-1-i)
            startScale=1
        elif numWhite>2 and startScale==1:
            endNum=(x-1-i)


    lent=startNum-endNum
    startX = endNum + int(lent / 3)
    endX = endNum + int(lent / 3) * 2
    startY = y-posYdelta
    endY=y
    scale = read_scale_number(
        orgImageDir+fileTo,
        (startX, startY),
        (endX, endY)
    )
    txtToWriteScaleLength += (fileName + '\t' +str(lent)+ '\n')
    txtToWriteScale += (fileName+'\t'+str(scale)+'\n')
    endTime = time.time()

    print(str(endTime - startTime))

with open(baseName+'_scale_length.txt', 'wt') as f:
    f.write(txtToWriteScaleLength)

with open(baseName+'_scale.txt', 'wt') as f:
    f.write(txtToWriteScale)