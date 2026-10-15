from PIL import Image
import numpy as np
import os
import time


def getFileName(fileName):
    lenFileName = len(fileName)
    nameEnd = 0
    nameStart = 0
    isDot = False

    for i in reversed(range(lenFileName)):
        if fileName[i] == '.':
            if isDot:
                continue
            else:
                nameEnd = i
                isDot = True

        if fileName[i] == '/':
            nameStart = i + 1
            break

    return fileName[nameStart:nameEnd]


def box_sum(binary, box_size):
    """
    각 pixel을 중심으로 box_size x box_size 영역 안의
    흰색 pixel 개수를 계산한다.
    """

    h, w = binary.shape

    half1 = box_size // 2
    half2 = box_size - half1

    # Integral image를 사용하여 빠르게 영역 내 pixel 수 계산
    integral = np.pad(
        binary,
        ((1, 0), (1, 0)),
        mode='constant'
    )

    integral = integral.cumsum(axis=0).cumsum(axis=1)

    yy = np.arange(h)
    xx = np.arange(w)

    y1 = np.maximum(yy - half1, 0)
    y2 = np.minimum(yy + half2, h)

    x1 = np.maximum(xx - half1, 0)
    x2 = np.minimum(xx + half2, w)

    sums = (
        integral[y2[:, None], x2[None, :]]
        - integral[y1[:, None], x2[None, :]]
        - integral[y2[:, None], x1[None, :]]
        + integral[y1[:, None], x1[None, :]]
    )

    return sums


def remove_isolated_mask(
    binary,
    box_size=50,
    min_white_pixels=50
):
    """
    독립적으로 떨어진 mask pixel 제거.

    단순히 현재 pixel을 중심으로 한 100x100 영역 하나만
    보는 것이 아니라,

        왼쪽 위 / 위 / 오른쪽 위
        왼쪽    / 중앙 / 오른쪽
        왼쪽 아래 / 아래 / 오른쪽 아래

    총 9개의 주변 영역을 검사한다.

    이 중 하나라도 흰색 pixel이 min_white_pixels보다 많으면
    main mass 주변에 있는 것으로 간주하여 유지한다.
    """

    h, w = binary.shape

    # 각 pixel 위치에서 100x100 안의 white pixel 수
    count_map = box_sum(binary, box_size)

    # window 중심을 50 pixel 정도씩 이동시켜 주변도 검사
    shift = box_size // 2

    offsets = (
        -shift,
        0,
        shift
    )

    max_count = np.zeros_like(count_map)

    for dy in offsets:
        for dx in offsets:

            shifted = np.zeros_like(count_map)

            src_y1 = max(0, -dy)
            src_y2 = min(h, h - dy)

            src_x1 = max(0, -dx)
            src_x2 = min(w, w - dx)

            dst_y1 = max(0, dy)
            dst_y2 = min(h, h + dy)

            dst_x1 = max(0, dx)
            dst_x2 = min(w, w + dx)

            shifted[
                dst_y1:dst_y2,
                dst_x1:dst_x2
            ] = count_map[
                src_y1:src_y2,
                src_x1:src_x2
            ]

            max_count = np.maximum(
                max_count,
                shifted
            )

    # 원래 흰색 pixel만 대상으로 한다.
    #
    # "100x100 안에 10 pixel 밖에 없으면 삭제"
    # → 10개 이하이면 제거
    #
    # 주변 9개 window 중 어느 하나라도 > 10이면 유지
    cleaned = binary & (
        max_count > min_white_pixels
    )

    return cleaned


################################################

baseName = 'hCS 37d HSY A2-14 A7-6 37d BrdU'

destImageDir = baseName + "_m/"
destImageDir2 = baseName + "_m2/"

os.makedirs(
    destImageDir2,
    exist_ok=True
)

################################################


maskFiles = os.listdir(destImageDir)

fileNum = 0
allFileNum = len(maskFiles)


for file in maskFiles:

    # 이미지 파일만 처리
    if not file.lower().endswith(
        (
            '.jpg',
            '.jpeg',
            '.png',
            '.tif',
            '.tiff',
            '.bmp'
        )
    ):
        continue

    fileNum += 1

    print(
        str(fileNum)
        + '/'
        + str(allFileNum)
    )

    startTime = time.time()

    ########################################
    # mask image 읽기
    ########################################

    maskImage = Image.open(
        destImageDir + file
    ).convert('L')

    maskArray = np.array(maskImage)

    ########################################
    # binary mask 생성
    ########################################

    # JPG는 compression 때문에
    # white가 정확히 255가 아닐 수 있으므로
    # 128 이상을 white로 간주
    binary = (
        maskArray > 128
    ).astype(np.uint8)

    ########################################
    # isolated pixel 제거
    ########################################

    cleaned = remove_isolated_mask(
        binary,
        box_size=50,
        min_white_pixels=50
    )

    ########################################
    # 다시 0 / 255 mask로 변환
    ########################################

    resultArray = (
        cleaned * 255
    ).astype(np.uint8)

    imM = Image.fromarray(
        resultArray,
        mode='L'
    ).convert('RGB')

    ########################################
    # 파일 이름
    ########################################

    fileName = getFileName(file)

    # _m 폴더 파일이
    # xxx-m.jpg인 경우
    # xxx-m-m.jpg가 되는 것을 방지
    if fileName.endswith('-m'):
        fileName = fileName[:-2]

    ########################################
    # 저장
    ########################################

    imM.save(
        destImageDir2
        + fileName
        + '-m.jpg',
        quality=100,
        subsampling=0
    )

    endTime = time.time()

    print(
        "elapsed:",
        str(endTime - startTime)
    )