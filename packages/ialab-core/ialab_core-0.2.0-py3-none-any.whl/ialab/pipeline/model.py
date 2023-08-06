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


class YoloV3(Processor):
    def __init__(self, cfg, weights, names, outputs=[]):
        Processor.__init__(self, outputs)
        self.net = cv.dnn.readNet(cfg, weights)
        with open(names, 'r') as f:
            self.classes = [c.strip() for c in f.readlines()]

    def _evaluate(self):
        layer_names = self.net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        return self.net.forward(output_layers)

    def __call__(self, image):
        Width = image.shape[1]
        Height = image.shape[0]
        scale = 0.00392

        blob = cv.dnn.blobFromImage(image, scale, (416,416), (0, 0, 0), True, crop=True)
        # blob = cv.dnn.blobFromImage(image, scale, (608,608), (0, 0, 0), True, crop=True)

        class_ids = []
        confidences = []
        boxes = []
        conf_threshold = 0.8
        nms_threshold = 0.7

        self.net.setInput(blob)
        outs = self._evaluate()

        result = []

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.9:
                    center_x = int(detection[0] * Width)
                    center_y = int(detection[1] * Height)
                    w = int(detection[2] * Width)
                    h = int(detection[3] * Height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])

        indices = cv.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

        for i in indices:
            i = i[0]
            x = boxes[i][0]
            y = boxes[i][1]
            w = boxes[i][2]
            h = boxes[i][3]
            class_id = class_ids[i]
            result.append(((int(y), int(x + w), int(y + h), int(x)), self.classes[class_id]))

        self.deliver((image, result))