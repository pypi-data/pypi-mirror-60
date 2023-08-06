from ialab.pipeline.model import Processor
import face_recognition
import os
import cv2 as cv
import numpy as np


class FaceExtractor(Processor):
    """
    Given an image and a set of bounding boxes cut each of the bounding boxes providing for
    the next Processor a list of images.
    """
    def __init__(self, outputs=[]):
        Processor.__init__(self, outputs)

    def __call__(self, data):
        image = data['image']
        regions = data['regions']
        images = [ (image[top:bottom,left:right], name) for ((top, right, bottom, left), name) in regions]
        self.deliver({'images': images})


class Skiper(object):
    def __init__(self, n_frames=1):
        self.n_frames = n_frames
        self.counter = self.n_frames - 1

    def should_execute(self):
        self.counter = (self.counter + 1) % self.n_frames
        return self.counter == 0

    def set_result(self, result):
        self.result = result

    def get_result(self, image):
        return {'image': image, 'regions': self.result}


class FaceRecognition(Processor):
    """
    Allows to load a face database from file images and then is able to run face
    recognition over images providing the bounding box for the image together with
    the person identity as well as the provided image

    Delivers: (image, [(location, name), . . .])
    """
    def __init__(self, paths='', outputs=[], skiper=Skiper(1)):
        """
        :param paths: Folder with the faces images for each person. The name of the file is the name of the person.
        :param outputs: Next processors in the pipe
        :param every_n_frames: Number of frames to wait before running detection again.
        :param skiper: Number of frames to wait before running detection again.
        """
        Processor.__init__(self, outputs)
        self.faces = []
        self.face_name = []
        self.result = []
        self.skiper = skiper

        for r, d, f in os.walk(paths):
            for file in f:
                image = face_recognition.load_image_file(os.path.join(r, file))
                locations = face_recognition.face_locations(image, model='cnn')
                if locations is not None and len(locations) > 0:
                    encoding = face_recognition.face_encodings(image, locations)[0]
                    self.faces.append(encoding)
                    self.face_name.append(file.replace('.jpeg', ''))

    def __call__(self, data):
        image = data['image']
        if self.skiper.should_execute():
            locations = face_recognition.face_locations(image, model='cnn')
            if locations is not None and len(locations) > 0:
                encodings = face_recognition.face_encodings(image, locations)
                encodings = zip(encodings, locations)
                result = []

                for encoding, location in encodings:
                    if len(self.faces) > 0:
                        truth = face_recognition.compare_faces(encoding, self.faces, tolerance=0.5)
                    else:
                        truth = []

                    if not True in truth:
                        result.append((location, 'unknown'))
                    else:
                        result.append((location, self.face_name[truth.index(True)]))
            else:
                result = None

            self.skiper.set_result(result)

        self.deliver(self.skiper.get_result(image))


class YoloV3(Processor):
    def __init__(self, cfg, weights, names, outputs=[], skiper=Skiper(1)):
        Processor.__init__(self, outputs)
        self.skiper = skiper
        self.net = cv.dnn.readNet(cfg, weights)
        with open(names, 'r') as f:
            self.classes = [c.strip() for c in f.readlines()]

    def _evaluate(self):
        layer_names = self.net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        return self.net.forward(output_layers)

    def __call__(self, data):
        image = data['image']
        if self.skiper.should_execute():
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

            self.skiper.set_result(result)

        self.deliver(self.skiper.get_result(image))