import os
import cv2 as cv


class VideoInput:
    def __init__(self, size, listeners):
        self.listeners = listeners
        self.finish = False
        self.size = size
        self.factored = False
        self.cap = None

    def __notify_listeners__(self, image):
        for l in self.listeners:
            l(image)

    def run(self):
        while not self.finish:
            self.runOne()

    def runOne(self):
        ret, image = self.cap.read()
        if ret:
            if not self.factored:
                x_factor =  image.shape[0] / self.size[0]
                y_factor = image.shape[1] / self.size[1]
                factor = max(x_factor, y_factor)
                self.size = (int(image.shape[1] / factor), int(image.shape[0] / factor))
                self.factored = True

            image = cv.resize(image, self.size, image)
            self.__notify_listeners__(image)


class ImageInput(VideoInput):
    def __init__(self, paths, size, listeners):
        super(ImageInput, self).__init__(size, listeners)
        self.paths = paths

    def run(self):
        for r, d, f in os.walk(self.paths):
            for file in f:
                self.__notify_listeners__(cv.imread(os.path.join(r, file)))


class CameraInput(VideoInput):
    def __init__(self, size, listeners):
        super(CameraInput, self).__init__(size, listeners)
        self.cap = cv.VideoCapture(0)
