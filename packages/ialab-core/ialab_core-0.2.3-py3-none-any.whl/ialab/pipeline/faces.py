from ialab.pipeline.model import Processor
import face_recognition
import os


class FaceExtractor(Processor):
    """
    Given an image and a set of bounding boxes cut each of the bounding boxes providing for
    the next Processor a list of images.
    """
    def __init__(self, outputs=[]):
        Processor.__init__(self, outputs)

    def __call__(self, faces):
        image, regions = faces
        images = [ (image[top:bottom,left:right], name) for ((top, right, bottom, left), name) in regions]
        self.deliver(images)


class FaceRecognition(Processor):
    """
    Allows to load a face database from file images and then is able to run face
    recognition over images providing the bounding box for the image together with
    the person identity as well as the provided image

    Delivers: (image, [(location, name), . . .])
    """
    def __init__(self, paths='', outputs=[], every_n_frames=1):
        """

        :param paths: Folder with the faces images for each person. The name of the file is the name of the person.
        :param outputs: Next processors in the pipe
        :param every_n_frames: Number of frames to wait before running detection again.
        """
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
                if locations is not None and len(locations) > 0:
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