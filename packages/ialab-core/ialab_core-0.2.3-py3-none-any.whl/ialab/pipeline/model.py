import cv2 as cv
import numpy as np


class Processor:
    def __init__(self, outputs=[]):
        self.outputs = outputs

    def add_output(self, output):
        self.outputs.append(output)

    def deliver(self, output):
        for o in self.outputs:
            o(output)


class RegionInPaintProcessor(Processor):
    """
    Given an image and a set of bounding boxes paints over the input image the
    bounding boxes.

    Expects as input (image, [ ((top, left, bottom, right), . . .), . . . ]
    Outputs: Only the input image
    """
    def __init__(self, outputs = []):
        Processor.__init__(self,outputs=outputs)

    def __call__(self, data):
        image, regions = data

        if regions is not None:
            for region in regions:
                image = cv.rectangle(image, (region[0][3], region[0][0]), (region[0][1], region[0][2]), (0,0,0), 3)
                image = cv.putText(image, region[1], fontFace=2, fontScale=1, org=(region[0][3], region[0][0] + 20), color=(0,0,0))

        self.deliver(image)


class KeyWait(Processor):
    """
    This should be used if you want to be able to see the result of a processing step before moving to
    the next one. This is mainly useful for debug purposes. This class is supposed to wait only in the
    context of OpenCV.
    """
    def __init__(self):
        Processor.__init__(self, [])

    def __call__(self, *args, **kwargs):
        cv.waitKey(0)


class ParallelProcessor(Processor):
    def __init__(self, processor, outputs = []):
        Processor.__init__(self, outputs=outputs)


def extract_parameter(index, processor):
    """
    This should be used when a processor in the chain receives just one
    parameter instead of tuple and you need just one of the tuple elements
    :param index:
    :param processor:
    :return:
    """
    def wrapper(parameter):
        processor(parameter[index])

    return wrapper


def add_parameter(index, constant, processor):
    """
    This should be used when a processor in the chain receives a tuple
    parameter instead of a single value and you need to expand it to a tuple
    :param index:
    :param processor:
    :return:
    """
    def wrapper(parameter):
        processor((parameter, constant))

    return wrapper
