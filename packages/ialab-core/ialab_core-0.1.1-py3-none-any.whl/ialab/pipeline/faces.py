from ialab.pipeline.model import Processor
import face_recognition
import os


class FaceExtractor(Processor):
    def __init__(self, outputs=[]):
        Processor.__init__(self, outputs)

    def __call__(self, faces):
        image, regions = faces
        images = [ (image[top:bottom,left:right], name) for ((top, right, bottom, left), name) in regions]
        self.deliver(images)


class FaceRecognition(Processor):
    def __init__(self, paths='', outputs=[], every_n_frames=1):
        Processor.__init__(self, outputs)
        self.every_n_frames = every_n_frames
        self.faces = []
        self.face_name = []
        self.frame = 0
        self.result = []

        for r, d, f in os.walk(paths):
            for file in f:
                image = face_recognition.load_image_file(os.path.join(r, file))
                locations = face_recognition.face_locations(image, model='cnn')
                encoding = face_recognition.face_encodings(image, locations)[0]
                self.faces.append(encoding)
                self.face_name.append(file.replace('.jpeg', ''))

    def __call__(self, image):
        self.frame = (self.frame + 1) % self.every_n_frames

        if self.frame == 1 or self.every_n_frames == 1:
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

            self.result = result
        else:
            result = self.result

        self.deliver((image, result))