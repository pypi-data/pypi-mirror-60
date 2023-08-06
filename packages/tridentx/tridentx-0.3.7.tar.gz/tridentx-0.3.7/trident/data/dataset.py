import os
import itertools
from typing import List, TypeVar, Iterable, Tuple, Union
from enum import Enum, unique
import numpy as np
from skimage import color
from .image_common import gray_scale, image2array, image_backend_adaptive
from .label_common import label_backend_adaptive
from .samplers import *

__all__ = ['DataType', 'DataRole', 'ExpectImageType', 'GetImageMode', 'Dataset', 'ImageDataset', 'LabelDataset',
           'IterableDataset', 'NumpyDataset']

T = TypeVar('T', int, float, str, np.ndarray)


class DataType(Enum):
    table = 'table'
    image = 'image'
    image_path = 'image_path'
    array = 'array'
    text = 'text'


class DataRole(Enum):
    input = 'input'
    target = 'target'
    mask = 'mask'


class ExpectImageType(Enum):
    gray = 'gray'
    rgb = 'rgb'
    rgba = 'rgba'
    label = 'label'
    multi_channel = 'multi_channel'


class GetImageMode(Enum):
    path = 'path'
    raw = 'raw'
    expect = 'expect'
    processed = 'processed'

list
class Dataset(List):
    def __init__(self):
        super().__init__()

    def __add__(self, other):
        if other is not None and hasattr(other, '__iter__'):
            for item in other:
                if isinstance(item, (int, float, str, np.ndarray)):
                    super().append(item)

    def __len__(self):
        return super().__len__()


class ImageDataset(Dataset):
    def __init__(self, images=None, expect_image_type: ExpectImageType = ExpectImageType.rgb,
                 get_image_mode: GetImageMode = GetImageMode.processed):
        super().__init__()
        self.__add__(images)
        self.datatype = DataType.image
        self.expect_image_type = expect_image_type
        self.dtype = np.float32
        self.get_image_mode = get_image_mode
        self.image_transform_funcs = []

    def __getitem__(self, index: int):
        img = super().__getitem__(index)#self.pop(index)
        if isinstance(img, str) and self.get_image_mode == GetImageMode.path:
            return img
        elif self.get_image_mode == GetImageMode.path:
            return None

        if isinstance(img, str):
            img = image2array(img)

        if self.get_image_mode == GetImageMode.raw:
            return img
        if not isinstance(img, np.ndarray):
            raise ValueError('image data should be ndarray')
        elif isinstance(img, np.ndarray) and img.ndim not in [2, 3]:
            raise ValueError('image data dimension  should be 2 or 3, but get {0}'.format(img.ndim))
        elif self.expect_image_type == ExpectImageType.gray:
            img = color.rgb2gray(img).astype(self.dtype)
        elif self.expect_image_type == ExpectImageType.rgb and img.ndim == 2:
            img = np.repeat(np.expand_dims(img, -1), 3, -1).astype(self.dtype)
        elif self.expect_image_type == ExpectImageType.rgb and img.ndim == 3:
            img = img[:, :, :3].astype(self.dtype)
        elif self.expect_image_type == ExpectImageType.rgba:
            if img.ndim == 2:
                img = np.repeat(np.expand_dims(img, -1), 3, -1)
            if img.shape[2] == 3:
                img = np.concatenate([img, np.ones((img.shape[0], img.shape[1], 1)) * 255], axis=-1)
            img = img.astype(self.dtype)
        elif self.expect_image_type == ExpectImageType.label:
            img = img.astype(np.uint8)
        elif self.expect_image_type == ExpectImageType.multi_channel:
            img = img.astype(self.dtype)

        if self.get_image_mode == GetImageMode.expect:
            return image_backend_adaptive(img)
        elif self.get_image_mode == GetImageMode.processed:
            return self.image_transform(img)

        return None

    def image_transform(self, img_data):
        if len(self.image_transform_funcs) == 0:
            return image_backend_adaptive(img_data)
        if isinstance(img_data, np.ndarray):
            # if img_data.ndim>=2:
            for fc in self.image_transform_funcs:
                img_data = fc(img_data)
            img_data = image_backend_adaptive(img_data)

            return img_data
        else:
            return img_data


class LabelDataset(Dataset):
    def __init__(self, labels=None, class_names=None):
        super().__init__()
        self.__add__(labels)
        self.datatype = DataType.array
        self.dtype = np.int64
        self.class_names = {}
        self._lab2idx = {}
        self._idx2lab = {}
        if class_names is not None:
            self.class_names = class_names

        self.label_transform_funcs = []

    def binding_class_names(self, class_names=None, language=None):
        if class_names is not None and hasattr(class_names, '__len__'):
            if language is None:
                language = 'en-us'
            self.class_names[language] = list(class_names)
            self.__default_language__ = language
            self._lab2idx = {v: k for k, v in enumerate(self.class_names[language])}
            self._idx2lab = {k: v for k, v in enumerate(self.class_names[language])}

    def __getitem__(self, index: int):
        label = super().__getitem__(index)
        return self.label_transform(label)

    def label_transform(self, label_data):
        label_data = label_backend_adaptive(label_data, self.class_names)
        if isinstance(label_data, list) and all(isinstance(elem, np.ndarray) for elem in label_data):
            label_data = np.asarray(label_data)
        if isinstance(label_data, np.ndarray):
            # if img_data.ndim>=2:
            for fc in self.label_transform_funcs:
                label_data = fc(label_data)
            return label_data
        else:
            return label_data


class NumpyDataset(Dataset):
    def __init__(self, data=None):
        super().__init__()

        self.__add__(data)
        self.datatype = DataType.array
        self.dtype = np.float32

    def __getitem__(self, index: int):
        data =super().__getitem__(index)
        return data


class IterableDataset(object):
    def __init__(self, data=None, label=None, mask=None, minibatch_size=8):
        self.data = NumpyDataset()
        self.label = LabelDataset()
        if data is not None and isinstance(data, Dataset):
            self.data = data
        if label is not None and isinstance(label, Dataset):
            self.label = label
        if mask is not None and isinstance(mask, Dataset):
            self.mask = mask

        self._minibatch_size = minibatch_size

        self.batch_sampler = BatchSampler(self, self._minibatch_size, is_shuffle=True, drop_last=False)
        self._sample_iter = iter(self.batch_sampler)

    @property
    def minibatch_size(self):
        return self._minibatch_size

    @minibatch_size.setter
    def minibatch_size(self, value):
        self._minibatch_size = value
        self.batch_sampler = BatchSampler(self, self._minibatch_size, is_shuffle=True, drop_last=False)
        self._sample_iter = iter(self.batch_sampler)

    def __getitem__(self, index: int):
        if len(self.label) == len(self.data) > 0:
            return self.data.__getitem__(index), self.label.__getitem__(index)
        return self.data.__getitem__(index)

    def _next_index(self):
        return next(self._sample_iter)

    def __iter__(self):
        return self._sample_iter

    def next(self):
        return next(self._sample_iter)

    def __next__(self):
        return next(self._sample_iter)

    def __len__(self):
        if self.data is not None:
            return len(self.data)
        else:
            return 0

