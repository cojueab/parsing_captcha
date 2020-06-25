import math
from PIL import Image
import hashlib


class _VectorCompare:

    @staticmethod
    def magnitude(concordance):
        total = 0
        for word, count in concordance.items():
          total += count ** 2
        return math.sqrt(total)

    def relation(self, concordance1, concordance2):
        relevance = 0
        topvalue = 0
        for word, count in concordance1.items():
          if word in concordance2:
            topvalue += count * concordance2[word]
        return topvalue / (self.magnitude(concordance1) * self.magnitude(concordance2))


def _buildvector(im):
    d1 = {}
    count = 0
    for i in im.getdata():
        d1[count] = i
        count += 1
    return d1


def _getimageset():
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    iconset = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+', '=']

    imageset = []
    import os
    for letter in iconset:
        temp = []
        temp.append(_buildvector(Image.open("%s/img/%s.gif" % (dir_path, letter))))
        imageset.append({letter: temp})
    return imageset


def parse(path):
    v = _VectorCompare()
    im = Image.open(path)
    im2 = Image.new("P", im.size, 255)
    im = im.convert("P")

    temp = {}

    for x in range(im.size[1]):
        for y in range(im.size[0]):
            pix = im.getpixel((y, x))
            temp[pix] = pix
            if pix in [1, 2, 3, 4, 5, 6, 7]:  # these are the numbers to get
                im2.putpixel((y, x), 0)

    inletter = False
    foundletter = False
    start = 0
    end = 0

    letters = []

    for y in range(im2.size[0]):  # slice across
        for x in range(im2.size[1]):  # slice down
            pix = im2.getpixel((y, x))
            if pix != 255:
                inletter = True

        if foundletter == False and inletter == True:
            foundletter = True
            start = y

        if foundletter == True and inletter == False:
            foundletter = False
            end = y
            letters.append((start, end))
        inletter = False
    count = 0
    result = ''
    imageset = _getimageset()
    for letter in letters:
        m = hashlib.md5()
        im3 = im2.crop((letter[0], 0, letter[1], im2.size[1]))

        guess = []

        for image in imageset:
            # print(image)
            for x, y in image.items():
                if len(y) != 0:
                    guess.append((v.relation(y[0], _buildvector(im3)), x))

        guess.sort(reverse=True)
        result += guess[0][1]
        count += 1
    return eval(result[:-1])
