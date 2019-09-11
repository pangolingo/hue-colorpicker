import time
import cv2
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from phue import Bridge
import random
import getch
import pdb


def main():
    cap = cv2.VideoCapture(0)

    while True:
        _, frame = cap.read()
        (frame_height, frame_width) = frame.shape[:2]
        w = 300
        h = round(w / frame_width * frame_height)
        w2 = 32
        h2 = round(w2 / frame_width * frame_height)
        original_image = cv2.resize(frame, (w, h), interpolation = cv2.INTER_AREA)
        new_image = cv2.resize(frame, (w2, h2), interpolation = cv2.INTER_AREA)
        new_image = cv2.resize(new_image, (w, h), interpolation = cv2.INTER_NEAREST)

        # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        # edges = cv2.dilate(cv2.Canny(original_image,w,h), kernel, iterations=1)
        edges = cv2.Canny(original_image,w,h)
        edges = cv2.bitwise_not(edges)
        edges2 = cv2.bitwise_and(original_image, original_image, mask=edges)

        new_edge = cv2.resize(edges2, (w2, h2), interpolation = cv2.INTER_AREA)
        new_edge = cv2.resize(new_edge, (w, h), interpolation = cv2.INTER_NEAREST)

        cv2.imshow("image", np.hstack([original_image, new_image]))
        cv2.imshow("edges", edges)
        cv2.imshow("edges2", edges2)
        cv2.imshow("new_edge", new_edge)
        # cv2.imshow("image", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # time.sleep(1)

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()