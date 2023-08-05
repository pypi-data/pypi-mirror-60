import cv2
import os


class Reader:
    def __init__(self, width=400, height=400, path=os.getcwd()):
        self.width = width
        self.height = height

        self.path = path
        self.images = []
        self.valid_images = [".jpg", ".gif", ".png", ".tga"]

    def read_image_files(self):
        for img in os.listdir(self.path):
            ext = os.path.splitext(img)[1]
            if ext.lower() not in self.valid_images:
                continue
            self.images.append(img)

        return self.images
        # print(self.images)

        # if len(self.images) > 0:
        #     for i, img in enumerate(self.images):
        #         print(i, os.path.join(self.path, img))
        #         image = cv2.imread(os.path.join(self.path, img))
        #         cv2.imshow(f'Image {i + 1}', image)
        #         cv2.waitKey(0)

        cv2.destroyAllWindows()