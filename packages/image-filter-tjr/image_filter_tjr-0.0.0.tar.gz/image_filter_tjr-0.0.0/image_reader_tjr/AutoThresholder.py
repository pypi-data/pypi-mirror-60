import cv2
import os
import imutils
from .ImageReader import Reader


class AutoThresholder(Reader):
    def __init__(self, neighbors=25, c=15):
        Reader.__init__(self, neighbors, c)

        self.neighbors = neighbors
        self.C = c
        self.images = self.read_image_files()

    def auto_thresh(self):
        if len(self.images) > 0:
            # load the images
            for i, img in enumerate(self.images):
                image = cv2.imread(os.path.join(self.path, img))
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                blurred = cv2.GaussianBlur(gray, (7, 7), 0)
                thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV,
                                               self.neighbors, self.C)

                cv2.imshow("Auto Mean Thresholded", thresh)
                cv2.imshow("Original", image)
                cv2.waitKey(0)

            cv2.destroyAllWindows()
        else:
            print("No images in filepath!")
