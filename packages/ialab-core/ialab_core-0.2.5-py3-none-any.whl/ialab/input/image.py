import os
import cv2 as cv


class VideoInput:
    """
    Base class for any type of visual input
    """
    def __init__(self, size, listeners):
        """
        :param size: Size the frames are going to be. This means maximum on width or height not exact size as this will keep image aspect ratio.
        :param listeners: List of Processors that will receive this input
        """
        self.listeners = listeners
        self.finish = False
        self.size = size
        self.factored = False
        self.cap = None

    def __notify_listeners__(self, image):
        for l in self.listeners:
            l({'image': image})

    def run(self):
        """
        Call this to start the processing loop
        """
        while not self.finish:
            self.runOne()

    def runOne(self):
        ret, image = self.cap.read()
        image = self._resize_(image if ret else None)
        self.__notify_listeners__(image)

    def _resize_(self, image):
        if image is not None:
            if not self.factored:
                x_factor =  image.shape[0] / self.size[0]
                y_factor = image.shape[1] / self.size[1]
                factor = max(x_factor, y_factor)
                self.size = (int(image.shape[1] / factor), int(image.shape[0] / factor))
                self.factored = True

            image = cv.resize(image, self.size, image)

        return image


class ImageInput(VideoInput):
    """
    This class takes a folder as parameter and loops through every image file on it
    providing them one by one as frames until no more images are found
    """
    def __init__(self, paths, size, listeners):
        """

        :param paths: Folder to search images in
        :param size: Size the frames are going to be. This means maximum on width or height not exact size as this will keep image aspect ratio.
        :param listeners: List of Processors that will receive this input
        """
        super(ImageInput, self).__init__(size, listeners)
        self.paths = paths

    def run(self):
        for r, d, f in os.walk(self.paths):
            for file in f:
                self.__notify_listeners__(self._resize_(cv.imread(os.path.join(r, file))))


class CameraInput(VideoInput):
    """
    This class takes the camera as input.
    """
    def __init__(self, size, listeners, cam_id = 0):
        """

        :param size: Size the frames are going to be. This means maximum on width or height not exact size as this will keep image aspect ratio.
        :param listeners: List of Processors that will receive this input
        :param cam_id: Represent the opencv camera identifier for the system. Defaults to 0 which is the main camera.
        """
        super(CameraInput, self).__init__(size, listeners)
        self.cap = cv.VideoCapture(cam_id)
