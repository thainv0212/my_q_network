import dill
import numpy as np
import pickle
from duel_q_network import agent
from tensorflow.python.keras.activations import relu, linear

from datetime import datetime


class MyDenseLayer:
    weight = None
    bias = None
    activation = None

    def my_relu(self, x):
        return (x > 0) * x

    def my_linear(self, x):
        return x



    def __init__(self, layer=None):
        self.activation_functions = {
            relu: 'relu',
            linear: 'linear'
        }
        self.activation_remap = {
            'relu': self.my_relu,
            'linear': self.my_linear
        }
        if layer is not None:
            self.weight = layer.weights[0].numpy()
            self.bias = layer.bias.numpy()
            if layer.activation is not None:
                self.activation = self.activation_functions[layer.activation]

    def __call__(self, x):
        val = x.dot(self.weight) + self.bias
        if self.activation is not None:
            val = self.activation_remap[self.activation](val)
        return val

    def to_json(self):
        return {
            'weight': self.weight,
            'bias': self.bias,
            'activation': self.activation
        }

    @staticmethod
    def from_json(data):
        layer = MyDenseLayer()
        layer.weight = data['weight']
        layer.bias = data['bias']
        layer.activation = data['activation']
        return layer


class MyPyNetwork:
    layers = []

    def from_network(self, network):
        layers = network.layers
        for layer in layers:
            converted_layer = MyDenseLayer(layer)
            self.layers.append(converted_layer)

    def __call__(self, x):
        t1 = datetime.now()
        tmp = x
        for layer in self.layers[:-2]:
            tmp = layer(tmp)
        tmp = self.layers[-1](tmp)
        print(datetime.now() - t1)
        return tmp

    def dump(self, path):
        layers_data = []
        for layer in self.layers:
            layers_data.append(layer.to_json())
        pickle.dump(layers_data, open(path, 'wb'))

    def dump_pkl(self, path):
        pickle.dump(self.layers, open(path, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)

    def load(self, path):
        # self.layers = dill.load(open(path, 'rb'))
        json_data = pickle.load(open(path, 'rb'))
        self.layers = []
        for d in json_data:
            self.layers.append(MyDenseLayer.from_json(d))


if __name__ == '__main__':
    my_agent = agent()
    my_agent.load_model()
    print('init agent')
    my_network = MyPyNetwork()
    my_network.from_network(my_agent.q_net)
    print('convert to numpy weights')
    my_network.dump('my_network.pickle')
    # my_network.dump_pkl('my_network.pickle')
    # my_network
    print('save to file')