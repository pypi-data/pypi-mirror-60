from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from enum import Enum, unique
import math
import os
import inspect
import numpy as np
from collections import *
from functools import partial
import uuid
from copy import copy, deepcopy
from collections import deque
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import init
from torch.nn.parameter import Parameter
from torch._six import container_abcs
from itertools import repeat


from ..backend.common import *
from ..backend.pytorch_backend import to_numpy,to_tensor,Layer,Sequential
from ..layers.pytorch_layers import *
from ..layers.pytorch_activations import  get_activation,Identity
from ..layers.pytorch_normalizations import get_normalization
from ..layers.pytorch_blocks import *
from ..layers.pytorch_pooling import *
from ..optims.pytorch_trainer import *
from ..data.image_common import *
from ..data.utils import download_file_from_google_drive

__all__ = ['gan_builder','UpsampleMode','BuildBlockMode']

_session = get_session()
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_epsilon=_session.epsilon
_trident_dir=_session.trident_dir


def resnet_block(num_filters=64,strides=1,expansion = 2,activation='leaky_relu', normalization='instance',dilation=1,name=''):
    shortcut = Identity()
    if strides > 1 or expansion!=1:
        shortcut = Conv2d_Block((1, 1), num_filters=int(num_filters*expansion), strides=strides, auto_pad=True,
                                padding_mode=PaddingMode.zero, normalization=normalization, activation=None,
                                name=name + '_downsample')


    return ShortCut2d(Sequential(Conv2d_Block((3,3),num_filters=num_filters//2,strides=strides,auto_pad=True,padding_mode=PaddingMode.reflection,normalization=normalization,activation=activation,dilation=dilation,name=name + '_conv1'),
                                 Conv2d_Block((1,1),num_filters=int(num_filters*expansion),strides=1,auto_pad=True,padding_mode=PaddingMode.reflection,normalization=normalization,activation=None,name=name + 'conv2')),
                      shortcut,activation=activation,name=name)




class UpsampleMode(Enum):
    pixel_shuffle = 'pixel_shuffle'
    transpose = 'transpose'
    nearest = 'nearest'
    bilinear = 'bilinear'

class BuildBlockMode(Enum):
    base = 'base'
    resnet = 'resnet'




def gan_builder(
        noise_shape=100,
        image_width=256,
        upsample_mode=UpsampleMode.pixel_shuffle,
        build_block_mode=BuildBlockMode.base,
        activation='leaky_relu',
        normalization='instance',
        use_dilation=False,
        use_dropout=False):

    noise_input=torch.tensor(data=np.random.normal(0, 1,size=noise_shape))

    def build_generator():
        layers=[]
        initial_size=8
        if image_width in [192,96,48]:
            initial_size=6
        elif image_width in [144,72,36]:
            initial_size = 9
        elif image_width in [160,80]:
            initial_size = 10
        layers.append(Dense(1024*initial_size*initial_size, activation=None,name='fc'))
        layers.append(Reshape((1024,initial_size, initial_size),name='reshape'))
        filter=1024
        current_width=initial_size
        i=1
        while current_width<image_width:
            scale = 2 if (image_width // current_width) % 2 == 0 else (image_width // current_width)
            dilation=1
            if use_dilation:
                dilation=2 if current_width>=64 else 1
            if upsample_mode==UpsampleMode.transpose:
                layers.append(TransConv2d_Block((3,3),max(filter//2,64),strides=scale,auto_pad=True,use_bias=False,activation=activation,normalization=normalization,dilation=dilation,name='transconv_block{0}'.format(i)))
            else:
                layers.append(Upsampling2d(scale_factor=scale,mode=upsample_mode.value,name='{0}{1}'.format(upsample_mode.value,i)))
            if build_block_mode == BuildBlockMode.base:
                layers.append(Conv2d_Block((3, 3), max(filter // 2, 64), strides=1, auto_pad=True, use_bias=False, activation=activation, normalization=normalization,dilation=dilation,name='base_block{0}'.format(i)))
            elif build_block_mode == BuildBlockMode.resnet:
                if upsample_mode != UpsampleMode.transpose:
                    layers.append(Conv2d((1, 1), max(filter // 2, 64), strides=1, auto_pad=True, use_bias=False, activation='activation',name='resnet_block{0}.prelayer'.format(i)))
                layers.append(resnet_block(max(filter // 2, 64), strides=1, expansion=1, activation=activation, normalization=normalization, dilation=dilation,name='resnet_block{0}'.format(i)))
            if current_width==32 and use_dropout:
                layers.append(Dropout(0.2))

            filter = max(filter // 2, 64)
            current_width = current_width*scale
            i=i+1
        layers.append( Conv2d((1, 1), 3, strides=1, auto_pad=True, use_bias=False, activation='tanh',name='last_layer'))
        return Sequential(layers,name='generator')


    def build_discriminator():
        layers = []
        layers.append(Conv2d((3, 3), 32, strides=1, auto_pad=True, use_bias=False, activation=activation))
        filter = 32
        current_width =image_width
        i=1
        while current_width >4:
            if build_block_mode == BuildBlockMode.base:
                layers.append(Conv2d_Block((3, 3), filter*2 if i>3 or i%2==1 else filter, strides=2, auto_pad=True, use_bias=False, activation=activation, normalization=normalization))
            elif build_block_mode == BuildBlockMode.resnet:
                layers.append(resnet_block(filter*2 if i>3 or i%2==1 else filter, strides=2, activation=activation, normalization=normalization))

            filter = filter*2 if i>3 or i%2==1 else filter
            current_width = current_width//2
            i = i + 1
        layers.append(Conv2d((3, 3), 1, strides=1, auto_pad=True, use_bias=False, activation=None))
        layers.append(Flatten())
        return Sequential(layers,name='discriminator')

    gen=ImageGenerationModel(input_shape=(noise_shape),output=build_generator())
    dis=ImageClassificationModel(input_shape=(3,image_width,image_width),output=build_discriminator())
    return gen,dis









