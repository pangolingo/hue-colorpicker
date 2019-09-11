import numpy as np
import cv2
import matplotlib.pyplot as plt

cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # gray = frame

    # move part of the image around
    # ball = gray[280:340, 330:390]
    # gray[273:333, 100:160] = ball

    # Crop from x, y, w, h -> 100, 200, 300, 400
    # NOTE: its img[y: y + h, x: x + w] and *not* img[x: x + w, y: y + h]
    crop_img = gray[200:400, 100:300] 

    im = crop_img
    # im = cv2.imread("toucans.jpg", cv2.IMREAD_GRAYSCALE)
    # params = cv2.SimpleBlobDetector_Params()
    detector = cv2.SimpleBlobDetector_create()
    # Detect blobs.
    keypoints = detector.detect(im)
    # Draw detected blobs as red circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)


    # dup the image
    dup_img = np.concatenate((im_with_keypoints, im_with_keypoints), axis=1)
    

    # Display the resulting frame
    # cv2.imshow('frame',dup_img)
    plt.imshow(dup_img)
    plt.show()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()