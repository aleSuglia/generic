import os
from PIL import Image

import numpy as np

from generic.data_provider.image_preprocessors import resize_image
from generic.utils.file_handlers import pickle_loader


# TODO make image loader more flexible (with crop)




class AbstractImgLoader(object):
    def __init__(self, img_dir):
        self.img_dir = img_dir

    def preload(self,picture_id):
        return self

    def get_image(self, picture_id):
        pass



class DummyImgLoader(AbstractImgLoader):
    def __init__(self, data_dir, size=1000):
        AbstractImgLoader.__init__(self, data_dir)
        self.size = size

    def get_image(self, _):
        return np.zeros(self.size)


"""Trick to avoid serializing complete fc8 dictionary.
We wrap the fc8 into a separate object which does not contain
the fc8 dictionary.
"""
class fcPreloaded(AbstractImgLoader):
    def __init__(self, data_dir, fc8):
        AbstractImgLoader.__init__(self, data_dir)
        self.fc8 = fc8

    def get_image(self, _):
        return self.fc8


class fcLoader(AbstractImgLoader):
    def __init__(self, data_dir):
        AbstractImgLoader.__init__(self, data_dir)
        self.data_dir = data_dir
        self.image_path = data_dir + ".pkl"
        self.fc8_img = pickle_loader(self.image_path)

    def preload(self, picture_id):
        return fcPreloaded(self.data_dir, self.fc8_img[picture_id])


class ConvLoader(AbstractImgLoader):
    def __init__(self, data_dir):
        AbstractImgLoader.__init__(self, data_dir)
        self.image_path = os.path.join(data_dir, "{}.npz")

    def get_image(self, picture_id):
        return np.load(self.image_path.format(picture_id)['x'])


class RawImageLoader(AbstractImgLoader):
    def __init__(self, data_dir, width, height, channel=None, extension="jpg"):
        AbstractImgLoader.__init__(self, data_dir)
        self.image_path = os.path.join(self.img_dir, "{}."+extension)
        self.width = width
        self.height = height
        self.channel = channel

    def get_image(self, picture_id):
        img = Image.open(self.image_path.format(picture_id)).convert('RGB')

        img = resize_image(img, self.width , self.height)
        img = np.array(img, dtype=np.float32)

        if self.channel is not None:
            img -= self.channel[None, None, :]

        return img



