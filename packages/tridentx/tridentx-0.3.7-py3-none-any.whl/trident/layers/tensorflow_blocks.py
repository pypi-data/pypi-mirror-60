from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from functools import reduce
from functools import wraps
import math
import collections
import itertools
import numpy as np
import copy
import tensorflow as tf
import tensorflow.keras.backend as K
from tensorflow_core.python.keras.utils import conv_utils
from tensorflow.python.framework import tensor_shape
from tensorflow.python.keras.engine.input_spec import InputSpec
from tensorflow.python.keras.utils import generic_utils
from tensorflow.python.ops import nn_ops
from tensorflow.python.client import device_lib
from tensorflow.python.keras import layers as layer_module

from tensorflow.python.keras.engine.base_layer import Layer
from tensorflow.python.keras.engine import base_layer_utils
from tensorflow.python.keras.engine import input_layer
from tensorflow.python.keras.engine import training
from tensorflow.python.keras.engine import training_utils
from tensorflow.python.keras.utils import layer_utils
from tensorflow.python.keras.utils import tf_utils

from tensorflow.python.training.tracking import layer_utils as trackable_layer_utils
from tensorflow.python.util import nest
from tensorflow.python.util import tf_inspect
from tensorflow.python.util.tf_export import keras_export

from .tensorflow_activations import get_activation, Identity
from .tensorflow_pooling import get_pooling, GlobalAvgPool2d
from .tensorflow_normalizations import get_normalization
from .tensorflow_layers import *

from itertools import repeat
import inspect

from ..backend.common import *
from ..backend.tensorflow_backend import *
from tensorflow.python.training.tracking import base as trackable
from tensorflow.python.keras.engine import base_layer

_tf_data_format = 'channels_last'

__all__ = ['Conv2d_Block', 'TransConv2d_Block', 'ShortCut2d']

_session = get_session()


def get_layer_repr(layer):
    # We treat the extra repr like the sub-module, one item per line
    extra_lines = []
    if hasattr(layer, 'extra_repr') and callable(layer.extra_repr):
        extra_repr = layer.extra_repr()
        # empty string will be split into list ['']
        if extra_repr:
            extra_lines = extra_repr.split('\n')
    child_lines = []
    if isinstance(layer, (tf.keras.Model, tf.keras.Sequential)) and layer.layers is not None:
        for module in layer.layers:
            mod_str = repr(module)
            mod_str = addindent(mod_str, 2)
            child_lines.append('(' + module.name + '): ' + mod_str)
    lines = extra_lines + child_lines

    main_str = layer.__class__.__name__ + '('
    if lines:
        # simple one-liner info, which most builtin Modules will use
        if len(extra_lines) == 1 and not child_lines:
            main_str += extra_lines[0]
        else:
            main_str += '\n  ' + '\n  '.join(lines) + '\n'

    main_str += ')'
    return main_str


class Conv1d_Block(Sequential):
    def __init__(self, kernel_size=(3), num_filters=32, strides=1,input_shape=None,  auto_pad=True, activation='leaky_relu',
                 normalization=None, use_bias=False, dilation=1, groups=1, add_noise=False, noise_intensity=0.001,
                 dropout_rate=0, **kwargs):
        super(Conv1d_Block, self).__init__()
        if add_noise:
            noise = tf.keras.layers.GaussianNoise(noise_intensity)
            self.add(noise)
        self._conv = Conv1d(kernel_size=kernel_size, num_filters=num_filters, strides=strides,input_shape=input_shape, auto_pad=auto_pad,
                            activation=None, use_bias=use_bias, dilation=dilation, groups=groups)
        self.add(self._conv)

        self.norm = get_normalization(normalization)
        if self.norm is not None:
            self.add(self.norm)

        self.activation = get_activation(snake2camel(activation))
        if self.activation is not None:
            self.add(self.activation)
        if dropout_rate > 0:
            self.drop = Dropout(dropout_rate)
            self.add(self.drop)




class Conv2d_Block(Sequential):
    def __init__(self, kernel_size=(3, 3), num_filters=32, strides=1, input_shape=None, auto_pad=True, activation='leaky_relu',
                 normalization=None, use_bias=False, dilation=1, groups=1, add_noise=False, noise_intensity=0.001,
                 dropout_rate=0,name='', **kwargs):
        super(Conv2d_Block, self).__init__( name=name)
        layers=[]
        self.add_noise=add_noise
        self.noise_intensity=noise_intensity
        if self.add_noise:
            self.add(Noise(stddev=noise_intensity))


        self.conv=Conv2d(kernel_size=kernel_size, num_filters=num_filters, strides=strides, auto_pad=auto_pad,activation=None, use_bias=use_bias, dilation=dilation, groups=groups,name=self.name+'_conv')
        if input_shape is not None:
            self.build(input_shape)
        self.add(self.conv)


        self.norm = get_normalization(normalization)
        if self.norm is not None:
            self.add(self.norm)
        self.activation = get_activation(snake2camel(activation))
        if self.activation is not None:
            self.add(self.activation)

        self.drop=None
        if dropout_rate > 0:
            if self.activation is not None:
                self.add(Dropout(dropout_rate))



    def get_config(self):
        config = {
            "add_noise":self.add_noise,
            "noise_intensity":self.noise_intensity,
            "conv":generic_utils.serialize_keras_object(self.conv),
            'norm': self.norm,
            'activation': self.activation,
            'drop':  self.drop
        }
        base_config = super(Conv2d_Block, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))
    #
    # @property
    # def conv(self):
    #     return self._conv
    #
    # @conv.setter
    # def conv(self, value):
    #     self._conv = value

# class Conv2d_Block1(tf.keras.layers.Layer):
#     def __init__(self, k, exp, out, SE, NL, s, l2, name="Conv2d_Block1", **kwargs):
#         super(Conv2d_Block1, self).__init__(name=name, **kwargs)
#         self.k = k
#         self.exp = exp
#         self.out = out
#         self.se = SE
#         self.nl = NL
#         self.s = s
#         self.l2 = l2
#         self.conv2d = tf.keras.layers.Conv2D(filters=out, kernel_size=k, strides=s, activation=None, padding="same",
#                                              kernel_regularizer=tf.keras.regularizers.l2(l2), name="conv2d", **kwargs)
#         self.bn = tf.keras.layers.BatchNormalization(momentum=0.99, name="BatchNormalization", **kwargs)
#         self.act = _available_activation[NL]
#
#     def call(self, input):
#         output = self.conv2d(input)
#         output = self.bn(output)
#         output = self.act(output)
#         return output
#
#     def get_config(self):
#         config = {"k":self.k, "exp":self.exp, "out":self.out, "SE":self.se, "NL":self.nl, "s":self.s, "l2":self.l2}
#         base_config = super(Conv2d_Block1, self).get_config()
#         return dict(list(base_config.items()) + list(config.items()))

class Conv3d_Block(Sequential):
    def __init__(self, kernel_size=(3, 3, 3), num_filters=32, strides=1,input_shape=None, auto_pad=True, activation='leaky_relu',
                 normalization=None, use_bias=False, dilation=1, groups=1, add_noise=False, noise_intensity=0.001,
                 dropout_rate=0, **kwargs):
        super(Conv3d_Block, self).__init__()
        if add_noise:
            noise = tf.keras.layers.GaussianNoise(noise_intensity)
            self.add(noise)
        self._conv = Conv3d(kernel_size=kernel_size, num_filters=num_filters, strides=strides,input_shape=input_shape, auto_pad=auto_pad,
                            activation=None, use_bias=use_bias, dilation=dilation, groups=groups)
        self.add(self._conv)

        self.norm = get_normalization(normalization)
        if self.norm is not None:
            self.add(self.norm)

        self.activation = get_activation(snake2camel(activation))
        if self.activation is not None:
            self.add(self.activation)
        if dropout_rate > 0:
            self.drop = Dropout(dropout_rate)
            self.add(self.drop)

    @property
    def conv(self):
        return self._conv

    @conv.setter
    def conv(self, value):
        self._conv = value


#
# class TransConv1d_Block(Sequential):
#     def __init__(self, kernel_size=(3), num_filters=32, strides=1, auto_pad=True,activation='leaky_relu',normalization=None,  use_bias=False,dilation=1, groups=1,add_noise=False,noise_intensity=0.001,dropout_rate=0, **kwargs ):
#         super(TransConv1d_Block, self).__init__()
#         if add_noise:
#             noise = tf.keras.layers.GaussianNoise(noise_intensity)
#             self.add(noise)
#         self._conv = TransConv1d(kernel_size=kernel_size, num_filters=num_filters, strides=strides, auto_pad=auto_pad,
#                       activation=None, use_bias=use_bias, dilation=dilation, groups=groups)
#         self.add(self._conv)
#
#         self.norm = get_normalization(normalization)
#         if self.norm is not None:
#             self.add(self.norm)
#
#         self.activation = get_activation(activation)
#         if self.activation is not None:
#             self.add(activation)
#         if dropout_rate > 0:
#             self.drop = Dropout(dropout_rate)
#             self.add(self.drop)
#     @property
#     def conv(self):
#         return self._conv
#     @conv.setter
#     def conv(self,value):
#         self._conv=value
#
#
#     def __repr__(self):
#         return get_layer_repr(self)


class TransConv2d_Block(Sequential):
    def __init__(self, kernel_size=(3, 3), num_filters=32, strides=1,input_shape=None, auto_pad=True, activation='leaky_relu',
                 normalization=None, use_bias=False, dilation=1, groups=1, add_noise=False, noise_intensity=0.001,
                 dropout_rate=0, **kwargs):
        super(TransConv2d_Block, self).__init__()
        if add_noise:
            noise = tf.keras.layers.GaussianNoise(noise_intensity)
            self.add(noise)
        self._conv = TransConv2d(kernel_size=kernel_size, num_filters=num_filters, strides=strides,input_shape=input_shape, auto_pad=auto_pad,
                                 activation=None, use_bias=use_bias, dilation=dilation, groups=groups)
        self.add(self._conv)

        self.norm = get_normalization(normalization)
        if self.norm is not None:
            self.add(self.norm)

        self.activation = get_activation(snake2camel(activation))
        if self.activation is not None:
            self.add(self.activation)
        if dropout_rate > 0:
            self.drop = Dropout(dropout_rate)
            self.add(self.drop)

    @property
    def conv(self):
        return self._conv

    @conv.setter
    def conv(self, value):
        self._conv = value


class TransConv3d_Block(Sequential):
    def __init__(self, kernel_size=(3, 3, 3), num_filters=32, strides=1, input_shape=None,auto_pad=True, activation='leaky_relu',
                 normalization=None, use_bias=False, dilation=1, groups=1, add_noise=False, noise_intensity=0.001,
                 dropout_rate=0, **kwargs):
        super(TransConv3d_Block, self).__init__()
        if add_noise:
            noise = tf.keras.layers.GaussianNoise(noise_intensity)
            self.add(noise)
        self._conv = TransConv3d(kernel_size=kernel_size, num_filters=num_filters, strides=strides,input_shape=input_shape, auto_pad=auto_pad,
                                 activation=None, use_bias=use_bias, dilation=dilation, groups=groups)
        self.add(self._conv)

        self.norm = get_normalization(normalization)
        if self.norm is not None:
            self.add(self.norm)

        self.activation = get_activation(snake2camel(activation))
        if self.activation is not None:
            self.add(self.activation)
        if dropout_rate > 0:
            self.drop = Dropout(dropout_rate)
            self.add(self.drop)

    @property
    def conv(self):
        return self._conv

    @conv.setter
    def conv(self, value):
        self._conv = value


class Classifer1d(Sequential):
    def __init__(self, num_classes=10, is_multilable=False, classifier_type=ClassfierType.dense, **kwargs):
        super(Classifer1d, self).__init__()
        self.classifier_type = classifier_type
        self.num_classes = num_classes
        self.is_multilable = is_multilable
        if classifier_type == ClassfierType.dense:
            self.add(Flatten)
            self.add(Dense(num_classes, use_bias=False, activation='sigmoid'))
            if not is_multilable:
                self.add(SoftMax)
        elif classifier_type == ClassfierType.global_avgpool:
            self.add(Conv2d((1, 1), num_classes, strides=1, auto_pad=True, activation=None))
            self.add(GlobalAvgPool2d)
            if not is_multilable:
                self.add(SoftMax)

    def __repr__(self):
        return get_layer_repr(self)

#
# class ShortCut2d(Layer):
#     def __init__(self, *args, activation='relu', name="ShortCut2d", **kwargs):
#         """
#
#         Parameters
#         ----------
#         layer_defs : object
#         """
#         super(ShortCut2d, self).__init__(name=name, **kwargs)
#         self.activation = get_activation(activation)
#         self.has_identity = False
#         self.add_layer=Add()
#         for i in range(len(args)):
#             arg = args[i]
#             if isinstance(arg, (tf.keras.layers.Layer, list, dict)):
#                 if isinstance(arg, list):
#                     arg = Sequential(*arg)
#                     self.add(arg)
#                 elif isinstance(arg, dict) and len(args) == 1:
#                     for k, v in arg.items():
#                         if v is Identity:
#                             self.has_identity = True
#                         self.add(v)
#                 elif isinstance(arg, dict) and len(args) > 1:
#                     raise ValueError('more than one dict argument is not support.')
#                 elif arg is  Identity:
#                     self.has_identity = True
#                     self.add(arg)
#                 else:
#                     # arg.name='branch{0}'.format(i + 1)
#                     self.add(arg)
#         if len(self.layers) == 1 and self.has_identity == False:
#             self.add(Identity(name='Identity'))
#
#         # Add to the model any layers passed to the constructor.
#
#
#
#     @property
#     def layers(self):
#         return self._layers
#
#     def add(self, layer):
#         self._layers.append(layer)
#
#
#     def compute_output_shape(self, input_shape):
#         shape = input_shape
#         shape = self.layers[0].compute_output_shape(shape)
#         return shape
#
#     def call(self, inputs, training=None, mask=None):
#         x = enforce_singleton(inputs)
#         result=[]
#         if 'Identity' in self._layers:
#             result.append(x)
#         for layer in self._layers:
#             if layer is not Identity:
#                 out = layer(x)
#                 result.append(out)
#         result=self.add_layer(result)
#         if self.activation is not None:
#             result = self.activation(result)
#         return result
#
#     def __repr__(self):
#         return get_layer_repr(self)




class ShortCut2d(tf.keras.Model):
    def __init__(self, *args,activation=None,mode=ShortcutMode.add, **kwargs):
        super(ShortCut2d, self).__init__()
        self.activation = get_activation(activation)
        self.has_identity = False
        self.mode = mode if isinstance(mode, str) else mode.value

        for i in range(len(args)):
            arg = args[i]
            if isinstance(arg, (Layer, list, dict)):
                if isinstance(arg, list):
                    arg = Sequential(*arg)
                elif isinstance(arg, dict) and len(args) == 1:
                    for k, v in arg.items():
                        if isinstance(v, Identity):
                            self.has_identity = True
                            self.add(v)
                        else:

                            self.add(v)
                elif isinstance(arg, dict) and len(args) > 1:
                    raise ValueError('more than one dict argument is not support.')
                elif isinstance(arg, Identity):
                    self.has_identity = True
                    self.add(arg)
                else:
                    self.add(arg)


        if len(self.layers) == 1 and self.has_identity == False:
            self.add(Identity())

    @property
    def layers(self):
        # Historically, `sequential.layers` only returns layers that were added
        # via `add`, and omits the auto-generated `InputLayer` that comes at the
        # bottom of the stack.
        # `Trackable` manages the `_layers` attributes and does filtering
        # over it.
        layers = super(ShortCut2d, self).layers
        if layers and isinstance(layers[0], input_layer.InputLayer):
            return layers[1:]
        return layers[:]

    @trackable.no_automatic_dependency_tracking
    def add(self, layer):
        """Adds a layer instance on top of the layer stack.

        Arguments:
            layer: layer instance.

        Raises:
            TypeError: If `layer` is not a layer instance.
            ValueError: In case the `layer` argument does not
                know its input shape.
            ValueError: In case the `layer` argument has
                multiple output tensors, or is already connected
                somewhere else (forbidden in `Sequential` models).
        """
        # If we are passed a Keras tensor created by keras.Input(), we can extract
        # the input layer from its keras history and use that without any loss of
        # generality.
        if hasattr(layer, '_keras_history'):
            origin_layer = layer._keras_history[0]
            if isinstance(origin_layer, input_layer.InputLayer):
                layer = origin_layer

        if not isinstance(layer, base_layer.Layer):
            raise TypeError('The added layer must be '
                            'an instance of class Layer. '
                            'Found: ' + str(layer))

        tf_utils.assert_no_legacy_layers([layer])

        # This allows the added layer to broadcast mutations to the current
        # layer, which is necessary to ensure cache correctness.
        layer._attribute_sentinel.add_parent(self._attribute_sentinel)

        self.built = False
        set_inputs = False
        if not self._layers:
            if isinstance(layer, input_layer.InputLayer):
                # Corner case where the user passes an InputLayer layer via `add`.
                assert len(nest.flatten(layer._inbound_nodes[-1].output_tensors)) == 1
                set_inputs = True
            else:
                batch_shape, dtype = training_utils.get_input_shape_and_dtype(layer)
                if batch_shape:
                    # Instantiate an input layer.
                    x = input_layer.Input(batch_shape=batch_shape, dtype=dtype, name=layer.name + '_input')
                    # This will build the current layer
                    # and create the node connecting the current layer
                    # to the input layer we just created.
                    layer(x)
                    set_inputs = True

            if set_inputs:
                # If an input layer (placeholder) is available.
                if len(nest.flatten(layer._inbound_nodes[-1].output_tensors)) != 1:
                    raise ValueError('All layers in a Sequential model '
                                     'should have a single output tensor. '
                                     'For multi-output layers, '
                                     'use the functional API.')
                self.outputs = [nest.flatten(layer._inbound_nodes[-1].output_tensors)[0]]
                self.inputs = layer_utils.get_source_inputs(self.outputs[0])

        elif self.outputs:
            # If the model is being built continuously on top of an input layer:
            # refresh its output.
            output_tensor = layer(self.outputs[0])
            if len(nest.flatten(output_tensor)) != 1:
                raise TypeError('All layers in a Sequential model '
                                'should have a single output tensor. '
                                'For multi-output layers, '
                                'use the functional API.')
            self.outputs = [output_tensor]

        if self.outputs:
            # True if set_inputs or self._is_graph_network or if adding a layer
            # to an already built deferred seq model.
            self.built = True

        if set_inputs or self._is_graph_network:
            self._init_graph_network(self.inputs, self.outputs, name=self.name)
        else:
            self._layers.append(layer)
        if self._layers:
            self._track_layers(self._layers)



    def build(self, input_shape):
        if self._is_graph_network:
            self._init_graph_network(self.inputs, self.outputs, name=self.name)
        else:
            input_shape = tensor_shape.TensorShape(input_shape)
            last_dim = tensor_shape.dimension_value(input_shape[-1])
            for layer in self.layers:
                layer.build(input_shape)
        self.built = True

    def call(self, inputs,**kwargs):
        if self._is_graph_network:
            if not self.built:
                self._init_graph_network(self.inputs, self.outputs, name=self.name)
            #return super(ShortCut2d, self).call(inputs, **kwargs)
        outputs=[]  # handle the corner case where self.layers is empty
        for layer in self.layers:
            # During each iteration, `inputs` are the inputs to `layer`, and `outputs`
            # are the outputs of `layer` applied to `inputs`. At the end of each
            # iteration `inputs` is set to `outputs` to prepare for the next layer.

            if self.has_identity:
                outputs.append(inputs)
            if layer is Identity:
                pass
            else:
                outputs.append(layer(inputs, **kwargs))

        if not hasattr(self,'mode') or self.mode=='add':
            outputs=tf.keras.layers.Add()(outputs)
        elif self.mode=='dot':
            outputs =tf.keras.layers.Dot()(outputs)
        elif  self.mode == 'concate':
            outputs=tf.keras.layers.Concatenate(axis=-1)(outputs)
        else:
            raise ValueError('Not valid shortcut mode' )
        if self.activation is not None:
            outputs = self.activation(outputs)
        return outputs

    def compute_output_shape(self, input_shape):
        input_shape = tensor_shape.TensorShape(input_shape)
        input_shape = input_shape.with_rank_at_least(4)
        output_shapes=[]
        for layer in self.layers:
            shape = layer.compute_output_shape(input_shape)
            output_shapes.append(shape)
        if self.mode=='add' or self.mode=='dot' :
            output_shapes=list(set(output_shapes))
            if len(output_shapes)==1:
                return output_shapes[0]

        elif self.mode=='concate':
            output_shape=list(output_shapes[0])
            for shape in output_shapes[1:]:
                if output_shape[3] is None or shape[3] is None:
                    output_shape[3] = None
                    break
                output_shape[3] += shape[3]
            return tuple(output_shape)

    def get_config(self):
          layer_configs = []
          for layer in self.layers:
              layer_configs.append(generic_utils.serialize_keras_object(layer))
          # When constructed using an `InputLayer` the first non-input layer may not
          # have the shape information to reconstruct `Sequential` as a graph network.
          if (self._is_graph_network and layer_configs and 'batch_input_shape' not in layer_configs[0][
              'config'] and isinstance(self._layers[0], input_layer.InputLayer)):
              batch_input_shape = self._layers[0]._batch_input_shape
              layer_configs[0]['config']['batch_input_shape'] = batch_input_shape

          config ={
              'name': self.name,
              'activation':self.activation,
              'has_identity':self.has_identity,
              'mode':self.mode,
              'layers': copy.deepcopy(layer_configs)
          }
          return config
