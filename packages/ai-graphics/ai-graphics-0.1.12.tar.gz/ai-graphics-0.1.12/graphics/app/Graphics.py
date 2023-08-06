"""
Name : Graphics.py
Author  : Cash
Contact : tkggpdc2007@163.com
Time    : 2020-01-08 10:52
Desc:
"""

import cv2
import numpy as np


__all__ = ['alpha_compose',
           'alpha_to_white',
           'add_border',
           'erase_border',
           'alpha_nonzero',
           'hash_similarity',
           'histogram_similarity',
           'orb_similarity',
           'variance_similarity']

# 初始化ORB检测器
_orb = cv2.ORB_create()
# 提取并计算特征点
_bf = cv2.BFMatcher(cv2.NORM_HAMMING)


def alpha_compose(image, src, x, y):
    """
    图像alpha通道融合
    :param image: numpy data with 3\4 channels
    :param src: numpy data with 4 channels
    :param x: col
    :param y: row
    :return: numpy data with 4 channels
    """
    try:
        if len(image.shape) < 3:
            return image

        if len(src.shape) < 3 or src.shape[-1] < 4:
            return src

        if image.shape[-1] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
        width, height = image.shape[:2][::-1]
        w, h = src.shape[:2][::-1]

        x1, y1 = max(-x, 0), max(-y, 0)
        x2, y2 = min(width - x, w), min(height - y, h)
        src = src[y1:y2, x1:x2]
        alpha = np.expand_dims(src[:, :, 3] / 255.0, -1)

        x, y = max(x, 0), max(y, 0)
        w, h = src.shape[:2][::-1]
        image[y:y + h, x:x + w] = src * alpha + image[y:y + h, x:x + w] * (1 - alpha)

    except ValueError:
        pass

    return image


def alpha_to_white(image):
    if len(image.shape) < 3:
        return image
    elif image.shape[-1] < 4:
        return image

    alpha = np.expand_dims(image[:, :, 3] / 255.0, -1)
    new = np.ones((image.shape[0], image.shape[1], 3), dtype=np.uint8)
    image = image[:, :, :-1] * alpha + new * (1 - alpha) * 255

    return image.astype("uint8")


def add_border(image, border, color):
    """
    添加边框
    :param image: numpy data with 3 channers
    :param border: [up, down, left, right]
    :param color: (r, g, b)
    :return:
    """
    if len(image.shape) < 3:
        return image

    h, w, c = image.shape
    up, down, left, right = border
    if up < 0 or down < 0 or left < 0 or right < 0:
        return image
    height, width, channel = h + up + down, w + left + right, 3
    new = np.empty((height, width, channel))
    new[:, :] = color
    new[up:height - down, left:width - right] = image
    return new


def erase_border(image, border, color):
    """
    添加边框
    :param image: numpy data with 3 channels
    :param border: [up, down, left, right]
    :param color: (r, g, b)
    :return:
    """
    if len(image.shape) < 3:
        return image

    height, width, _ = image.shape
    up, down, left, right = border
    if up < 0 or down < 0 or left < 0 or right < 0:
        return image
    new = np.empty((height, width, 3))
    new[:, :] = color
    new[up:height - down, left:width - right] = image[up:height - down, left:width - right]
    return new.astype(np.uint8)


def alpha_nonzero(image):
    """
    处理图层图像，裁剪空白区域，保留最小凸包
    :param image:
    :return:
    """
    if len(image.shape) != 3 and image.shape[-1] != 4:
        return image
    x = np.nonzero(image[:, :, 3])
    c_min = min(x[1])
    c_max = max(x[1])
    r_min = min(x[0])
    r_max = max(x[0])
    return image[r_min:r_max + 1, c_min:c_max + 1]


def hash_similarity(image1, image2, type='dHash'):
    def a_hash(img):
        img = cv2.resize(img, (8, 8), interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        np_mean = np.mean(gray)
        value = (gray >= np_mean) + 0  # 大于平均值=1，否则=0
        value_list = value.reshape(1, -1)[0].tolist()  # 展平->转成列表
        value_str = ''.join([str(x) for x in value_list])
        return value_str

    def p_hash(img):
        img = cv2.resize(img, (32, 32))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.dct(np.float32(gray))
        gray = gray[0:8, 0:8]  # opencv实现的掩码操作
        np_mean = np.mean(gray)
        value = (gray > np_mean) + 0
        value_list = value.reshape(1, -1)[0].tolist()
        value_str = ''.join([str(x) for x in value_list])
        return value_str

    def d_hash(img):
        img = cv2.resize(img, (9, 8), interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 每行前一个像素大于后一个像素为1，相反为0，生成哈希
        hash_str = []
        for i in range(8):
            hash_str.append(gray[:, i] > gray[:, i + 1])
        hash_str = np.array(hash_str) + 0
        hash_str = hash_str.T
        hash_str = hash_str.reshape(1, -1)[0].tolist()
        hash_str = ''.join([str(x) for x in hash_str])
        return hash_str

    if type == 'aHash':
        s1, s2 = a_hash(image1), a_hash(image2)
    elif type == 'pHash':
        s1, s2 = p_hash(image1), p_hash(image2)
    else:
        s1, s2 = d_hash(image1), d_hash(image2)

    return sum([ch1 != ch2 for ch1, ch2 in zip(s1, s2)])


def histogram_similarity(image1, image2, size=(256, 256)):
    def calculate(image1, image2):
        hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
        hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])
        # 计算直方图的重合度
        degree = 0
        for i in range(len(hist1)):
            if hist1[i] != hist2[i]:
                degree = degree + (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
            else:
                degree = degree + 1
        degree = degree / len(hist1)
        return degree

    # 将图像resize后，分离为RGB三个通道，再计算每个通道的相似值
    image1 = cv2.resize(image1, size)
    image2 = cv2.resize(image2, size)
    sub_image1 = cv2.split(image1)
    sub_image2 = cv2.split(image2)
    sub_data = 0
    for im1, im2 in zip(sub_image1, sub_image2):
        sub_data += calculate(im1, im2)
    sub_data = sub_data / 3
    return sub_data


def orb_similarity(image1, image2):
    """
    :param image1: 图片1
    :param image2: 图片2
    :return: 图片相似度
    """
    try:
        h1, w1 = image1.shape[:2]
        h2, w2 = image2.shape[:2]
        r1 = min(min(h2 / h1, 1.), min(w2 / w1, 1.))
        r2 = min(min(h1 / h2, 1.), min(w1 / w2, 1.))
        image1 = cv2.resize(image1, (int(image1.shape[1] * r1), int(image1.shape[0] * r1)))
        image2 = cv2.resize(image2, (int(image2.shape[1] * r2), int(image2.shape[0] * r2)))

        kp1, des1 = _orb.detectAndCompute(image1, None)
        kp2, des2 = _orb.detectAndCompute(image2, None)
        # knn筛选结果
        matches = _bf.knnMatch(des1, des2, k=2)
        # 查看最大匹配点数目
        good = [[m] for (m, n) in matches if m.distance < 0.75 * n.distance]

        # _img1 = cv2.drawKeypoints(image1, kp1, None, color=(0, 255, 0), flags=0)
        # _img2 = cv2.drawKeypoints(image2, kp2, None, color=(0, 255, 0), flags=0)
        # _img3 = cv2.drawMatchesKnn(image1, kp1, image2, kp2, good, None, flags=2)
        # cv2.imwrite("1.png", _img1)
        # cv2.imwrite("2.png", _img2)
        # cv2.imwrite("3.png", _img3)

        return len(good) / len(matches)

    except ValueError:
        return 0


def variance_similarity(image1, image2, confident=0.8):
    def calculate(img):
        img = cv2.resize(img, (32, 32))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mses = []
        for i in range(32):
            avg = np.mean(gray[i, :])
            mse = np.square(gray[i, :] - avg)
            mses.append(mse)
        return np.array(mses)

    mses1, mses2 = calculate(image1), calculate(image2)
    diffs = np.abs(mses1, mses2)
    fingle = np.array(diffs < (1 - confident) * np.max(diffs)) + 0
    similar = fingle.reshape(1, -1)[0].tolist()
    similar = 1 if similar == 0.0 else sum(similar) / len(similar)

    return similar


# if __name__ == '__main__':
#     src = cv2.imread('27.png', cv2.IMREAD_UNCHANGED)
#     image = image_crop(src, (1080, 1080))
#     cv2.imwrite("27-1.png", image)
#     print(1)
#     img1 = cv2.imread('商品主图形_1.png', cv2.IMREAD_UNCHANGED)
#     img2 = cv2.imread('商品主图形_2.png', cv2.IMREAD_UNCHANGED)
#     s = orb_similarity(alpha_to_white(img1), alpha_to_white(img2))
#     print(s)
#     h = histogram_similarity(alpha_to_white(img1), alpha_to_white(img2))
#     print(h)
