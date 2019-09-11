import time
import cv2
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from phue import Bridge
import random
import getch
import pdb

b = Bridge('10.0.0.12')
b.connect()
GROUP = 3
artery_lights = b.get_group(GROUP, 'lights')
artery_lights = list(map(lambda l: int(l), artery_lights))
b.set_group(GROUP, 'on', True)

def change_light_color(bridge, light, color_xyY, brightness):
    print('changing light #{light} to {color}/{brightness}'.format(
        light=light,
        color=color_xyY,
        brightness=brightness
    ))
    # b.set_light(artery_lights[0], {
    #     'transitiontime': 10,
    #     'transitiontime': 150,
    #     'xy': (colocolor_xyYr[0], color_xyY[1]),
    #     'bri': brightness
    # })

# from https://www.pyimagesearch.com/2015/10/05/opencv-gamma-correction/
def adjust_gamma(image, gamma=1.0):
	# build a lookup table mapping the pixel values [0, 255] to
	# their adjusted gamma values
	invGamma = 1.0 / gamma
	table = np.array([((i / 255.0) ** invGamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")
 
	# apply gamma correction using the lookup table
	return cv2.LUT(image, table)

def draw_crosshairs(image):
    (h, w) = image.shape[:2]
    center = (round(w/2), round(h/2))
    white = (255, 255, 255)
    cv2.line(image, (center[0] - 10, center[1]), (center[0] - 30, center[1]), white, thickness=1, lineType=8, shift=0)
    cv2.line(image, (center[0] + 10, center[1]), (center[0] + 30, center[1]), white, thickness=1, lineType=8, shift=0)
    cv2.line(image, (center[0], center[1] - 10), (center[0], center[1] - 30), white, thickness=1, lineType=8, shift=0)
    cv2.line(image, (center[0], center[1] + 10), (center[0], center[1] + 30), white, thickness=1, lineType=8, shift=0)
    cv2.circle(image, center, 20, white, thickness=1, lineType=8, shift=0)

def XYZ_to_xyY(xyz):
    X = xyz[0] / 255
    Y = xyz[1] / 255
    Z = xyz[2] / 255
    sum = X + Y + Z

    if sum <= 0:
        # todo: should return reference white
        return (0,0)

    x = X / sum
    y = Y / sum
    Y = Y
    return (x, y, Y)

def main():
    # contains the kmeans cluster from the last frame
    # we'll reuse this to seed the next frame's cluster
    previous_cluster = None
    # reduce the image to this many colors
    num_colors = 5
    # begin capturing video from the webcam
    cap = cv2.VideoCapture(0)

    while True:
        # read a frame from the webcam
        _, frame = cap.read()
        frame = adjust_gamma(frame, 1.3)
        # reduce the size of the frame to avoid extra processing
        # frame = cv2.imread("toucans.jpg")
        (frame_height, frame_width) = frame.shape[:2]
        w = 300
        h = round(w / frame_width * frame_height)
        original_image = cv2.resize(frame, (w, h), interpolation = cv2.INTER_AREA)
        




        
        # convert the image from the RGB color space to the L*a*b*
        # color space -- since we will be clustering using k-means
        # which is based on the euclidean distance, we'll use the
        # L*a*b* color space where the euclidean distance implies
        # perceptual meaning
        image = cv2.cvtColor(original_image, cv2.COLOR_BGR2LAB)
        
        # reshape the image into a feature vector so that k-means
        # can be applied
        image = image.reshape((image.shape[0] * image.shape[1], 3))
        
        # apply k-means using the specified number of clusters and
        # then create the quantized image based on the predictions
        if previous_cluster is None:
            clt = MiniBatchKMeans(n_clusters=num_colors)
        else:
            clt = MiniBatchKMeans(n_clusters=num_colors, init=previous_cluster)
        labels = clt.fit_predict(image)
        # save the centers so we can can run it again and preseed with them
        previous_cluster = clt.cluster_centers_

        # the list of colors detected
        colors = clt.cluster_centers_.astype("uint8")
        # the image reduced to colors
        quant = clt.cluster_centers_.astype("uint8")[labels]

        # reshape the feature vectors to images
        quant = quant.reshape((h, w, 3))
        colors = colors.reshape((num_colors, 1, 3))

        # convert from L*a*b* to BRG (reverse RGB)
        quant = cv2.cvtColor(quant, cv2.COLOR_LAB2BGR)
        colors = cv2.cvtColor(colors, cv2.COLOR_LAB2BGR)

        # convert colors to HSV so we can order by saturation
        colors_ordered = cv2.cvtColor(colors, cv2.COLOR_BGR2HSV)
        # convert the 3d array to a 2d array, sort it on the second column (saturation)
        # flip it so the highest values are first, then convert it back to a 3d image array
        colors_ordered = np.reshape(colors_ordered, (5,3))
        colors_ordered = np.flip(colors_ordered[colors_ordered[:,1].argsort()], 0)
        colors_ordered = np.reshape(colors_ordered, (5,1,3))
        # colors_ordered = np.lexsort((colors_ordered[:, 1], colors_ordered[:, 0]))
        # colors_ordered.sort(key=lambda x: x[0])
        # dtype = [('h', int), ('s', int), ('v', int)]
        # colors_ordered = np.array(colors_ordered, dtype=dtype)
        # np.sort(colors_ordered, order='s')
        print(colors_ordered)
        colors_ordered = cv2.cvtColor(colors_ordered, cv2.COLOR_HSV2BGR)

        # show the colors (size the num_colors x 1px image up to 200x200)
        cv2.imshow("colors", cv2.resize(colors, (200, 200), interpolation = cv2.INTER_NEAREST))
        cv2.imshow("colors_ordered", cv2.resize(colors_ordered, (200, 200), interpolation = cv2.INTER_NEAREST))
        # show the original and modified webcam images
        cv2.imshow("image", np.hstack([original_image, quant]))

        # halt if the escape key is pressed
        key = cv2.waitKey(500)
        if key == 27:
            break

        # key = getch.getch()
        # if key == ' ':
        # space
        # if key == 32:
        if True:
            # convert the colors to XYZ values
            colors_XYZ = cv2.cvtColor(colors, cv2.COLOR_BGR2XYZ)
            # extract 2 colors and convert them to xyY
            color1 = XYZ_to_xyY(colors_XYZ[0][0])
            color2 = XYZ_to_xyY(colors_XYZ[1][0])

            # default to a brightness of 100
            # if the color contains a Y value (luminance) use that
            brightness1 = 100
            brightness2 = 100
            if len(color1) > 2:
                brightness1 = int(color1[2] * 255)
            if len(color2) > 2:
                brightness2 = int(color2[2] * 255)

            change_light_color(b, artery_lights[0], color1, brightness1)
            change_light_color(b, artery_lights[1], color2, brightness2)

        # wait 1s to give the hue time to recover
        time.sleep(1)

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()