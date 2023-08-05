import cv2
import os
import imutils
from .ImageReader import Reader


class Thresholder(Reader):
    def __init__(self, t=200, inv=False):
        Reader.__init__(self, t, inv)

        self.inv = inv
        self.T = t
        self.images = self.read_image_files()

    def thresh(self):
        if len(self.images) > 0:
            # load the images
            for i, img in enumerate(self.images):
                image = cv2.imread(os.path.join(self.path, img))
                # image = imutils.resize(image, width=self.width)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                blurred = cv2.GaussianBlur(gray, (7, 7), 0)
                if self.inv:
                    # if pixel value is more than 200, we set it to 0 for inverse thresholding
                    (_, threshInv) = cv2.threshold(blurred, self.T, 255, cv2.THRESH_BINARY_INV)
                    cv2.imshow("Inverse Thresholded", threshInv)
                else:
                    # if pixel value is more than 200, we set it to 255
                    (_, thresh) = cv2.threshold(blurred, self.T, 255, cv2.THRESH_BINARY)
                    cv2.imshow("Thresholded", thresh)

                cv2.imshow("Original", image)
                cv2.waitKey(0)

            cv2.destroyAllWindows()
        else:
            print("No images in filepath!")
