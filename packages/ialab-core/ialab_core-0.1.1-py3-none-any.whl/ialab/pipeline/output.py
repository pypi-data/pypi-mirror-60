from ialab.pipeline.model import Processor
import cv2 as cv
import os


class ShowImage(Processor):
    def __init__(self, title, enable_exit=True):
        Processor.__init__(self, [])
        self.title = title
        self.enable_exit = enable_exit

    def __call__(self, image):
        cv.imshow(self.title, image)

        if cv.waitKey(1) == 27 and self.enable_exit:
            exit()


class ImageWriter(Processor):
    def __init__(self, destination):
        Processor.__init__(self, [])
        self.destination = destination

    def __call__(self, images):
        for image, name in images:
            cv.imwrite(os.path.join(self.destination, name + '.jpeg'), image)