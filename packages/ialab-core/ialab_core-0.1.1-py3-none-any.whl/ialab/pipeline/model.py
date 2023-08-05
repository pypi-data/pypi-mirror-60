import cv2 as cv
import os


class Processor:
    def __init__(self, outputs=[]):
        self.outputs = outputs

    def add_output(self, output):
        self.outputs.append(output)

    def deliver(self, output):
        for o in self.outputs:
            o(output)


class RegionInPaintProcessor(Processor):
    def __init__(self, outputs = []):
        Processor.__init__(self,outputs=outputs)

    def __call__(self, data):
        image, regions = data

        for region in regions:
            image = cv.rectangle(image, (region[0][3], region[0][0]), (region[0][1], region[0][2]), (0,0,0), 3)

        self.deliver(image)