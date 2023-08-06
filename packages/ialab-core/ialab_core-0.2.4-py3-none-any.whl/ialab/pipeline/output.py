from ialab.pipeline.model import Processor
import cv2 as cv
import os


class ShowImage(Processor):
    """
    Given an input image this just displays it on screen.
    """
    def __init__(self, title, enable_exit=True):
        """
        :param title: Title of the image window
        :param enable_exit: Allows exit by pressing escape
        """
        Processor.__init__(self, [])
        self.title = title
        self.enable_exit = enable_exit

    def __call__(self, data):
        cv.imshow(self.title, data['image'])

        if cv.waitKey(1) == 27 and self.enable_exit:
            exit()


class ImageWriter(Processor):
    """
    Writes an input image into disk

    Expects as input: [(image, name), . . .]
    """
    def __init__(self, destination):
        """
        :param destination: Folder where to write the image
        """
        Processor.__init__(self, [])
        self.destination = destination

    def __call__(self, data):
        images = data.get(['images'], None)
        if images is not None:
            for image, name in images:
                cv.imwrite(os.path.join(self.destination, name + '.jpeg'), image)
        else:
            cv.imwrite(os.path.join(self.destination, data['name'] + '.jpeg'), data['image'])