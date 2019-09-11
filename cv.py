import cv2
import numpy as numpy
from matplotlib import pyplot


# read in the image
img = cv2.imread('toucans.jpg')

# read the BRG values of a pixel
px = img[100,100]
print(px)

# read just the blue (first) value of a pixel
blue = img[100,100,0]
print(blue)

# set the BRG value of a pixel
img[100,100] = [255,255,255]
print(img[100,100])

# set an individual value of a pixel
print(img.item(10,10,2))
img.itemset((10,10,2),100)
print(img.item(10,10,2))

# get # of pixel rows, columns, and channels
print(img.shape)

# total # of pixels
# width * height * 3 channels
print(img.size)

# print image type
print(img.dtype)

# capture an area, then move it to another area
# this does nothing because we don't write anything
ball = img[280:340, 330:390]
img[273:333, 100:160] = ball

# split an image into BGR channels
b,g,r  = cv2.split(img)
# merge it back to a full color image
img = cv2.merge((b,g,r))

# a better way is to use indexing
b = img[:,:,0]
# set all red pixels to 0
img[:,:,2] = 0

pyplot.subplot(231),pyplot.imshow(img,'gray'),pyplot.title('ORIGINAL')

pyplot.show()