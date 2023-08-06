import numpy as np

class Sequential:
    def __init__(self, input_size):
        self.layers = []
        self.input_size = input_size
        self.__current_input_size = input_size

    def add(self, layer):
        layer._create_weights(self.__current_input_size)
        self.layers.append(layer)
        self.__current_input_size = layer.dim_out

    def __call__(self, x):
        for layer in self.layers:
            x = layer(x)         
        return x

    def _backprop(self, grads, lr):
        for layer in self.layers[::-1]:
            grads = layer.grads(grads)
            layer._apply_grads(grads, lr)

    def summary(self):
        param_count = 0
        print('MODEL:')
        for layer in self.layers:
            param_count +=  layer._get_trainable_params()
            print(layer, '\ttrainable params : %d' % (layer._get_trainable_params()))
        print('Total trainable parameters : %d' % param_count)
    
    def fit(self):
        pass