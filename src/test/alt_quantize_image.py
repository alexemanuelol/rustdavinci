#!/usr/bin/env python3

# pip install scikit-image
# pip install scipy

import numpy as np
from PIL import Image
from skimage import color

def CIE76DeltaE2(Lab1,Lab2):
    """Returns the square of the CIE76 Delta-E colour distance between 2 lab colours"""
    return (Lab2[0]-Lab1[0])*(Lab2[0]-Lab1[0]) + (Lab2[1]-Lab1[1])*(Lab2[1]-Lab1[1]) + (Lab2[2]-Lab1[2])*(Lab2[2]-Lab1[2])

def NearestPaletteIndex(Lab,palLab):
    """Return index of entry in palette that is nearest the given colour"""
    NearestIndex = 0
    NearestDist   = CIE76DeltaE2(Lab,palLab[0,0])
    for e in range(1,palLab.shape[0]):
        dist = CIE76DeltaE2(Lab,palLab[e,0])
        if dist < NearestDist:
            NearestDist = dist
            NearestIndex = e
    return NearestIndex

palette = (
        46, 204, 113,   46, 157, 135,   39, 174, 96,    22, 160, 133,   29, 224, 25,
        52, 152, 218,   32, 203, 241,   74, 212, 189,   126, 76, 42,    68, 48, 34,
        241, 195, 15,   175, 122, 195,  240, 67, 49,    142, 68, 173,   230, 126, 34,
        152, 163, 163,  236, 240, 241,  49, 49, 49,     52, 73, 94,     2, 2, 2,

        91, 175, 118,   91, 144, 130,   89, 155, 109,   91, 148, 132,   87, 189, 86,
        93, 141, 185,   88, 174, 201,   99, 180, 164,   125, 100, 90,   98, 92, 88,
        202, 171, 90,   157, 126, 171,  202, 101, 96,   137, 102, 156,  195, 128, 93,
        143, 150, 150,  197, 200, 201,  92, 92, 92,     93, 100, 109,   84, 84, 84,

        111, 149, 121,  117, 138, 132,  116, 143, 123,  109, 134, 126,  110, 157, 109,
        111, 132, 155,  110, 149, 163,  114, 152, 144,  125, 114, 111,  113, 111, 110,
        163, 146, 109,  139, 123, 146,  155, 102, 99,   129, 113, 138,  159, 125, 110,
        137, 140, 140,  162, 163, 163,  111, 111, 111,  111, 114, 118,  109, 109, 109,

        126, 140, 129,  119, 127, 125,  126, 136, 128,  125, 134, 131,  126, 143, 125,
        120, 127, 136,  126, 139, 146,  127, 141, 138,  124, 120, 119,  120, 119, 119,
        146, 139, 125,  136, 130, 139,  145, 127, 126,  132, 127, 135,  138, 124, 119,
        127, 128, 128,  145, 145, 146,  119, 119, 119,  126, 127, 128,  119, 119, 119
) + (2, 2, 2) * 176

# Load the source image as numpy array and convert to Lab colorspace
imnp = np.array(Image.open('C:\\Users\\Alexander\\Downloads\\aaa.png').convert('RGB'))
imLab = color.rgb2lab(imnp) 
h,w = imLab.shape[:2]

# Load palette as numpy array, truncate unused palette entries, and convert to Lab colourspace
palnp = np.array(palette,dtype=np.uint8).reshape(256,1,3)[:80,:]
palLab = color.rgb2lab(palnp)

# Make numpy array for output image
resnp = np.empty((h,w), dtype=np.uint8)

# Iterate over pixels, replacing each with the nearest palette entry
for y in range(0, h):
    for x in range(0, w):
        resnp[y, x] = NearestPaletteIndex(imLab[y,x], palLab)

# Create output image from indices, whack a palette in and save
resim = Image.fromarray(resnp, mode='P')
resim.putpalette(palette)
#resim.save('result.png')
resim.show()
