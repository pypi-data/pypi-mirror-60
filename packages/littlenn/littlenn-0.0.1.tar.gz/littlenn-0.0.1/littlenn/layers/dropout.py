import numpy as np
from littlenn.layers.abstract_layer import Layer

class Dropout(Layer):
    def __init__(self, keep_prob):
        super(Dropout, self).__init__()
        self.keep_prob = keep_prob

    def _create_weights(self, dim_in):
        self.dim_in = dim_in
        self.dim_out = dim_in

        self.W = np.random.randn(self.dim_out, self.dim_in) < self.keep_prob

    def _get_weights(self):
        return self.W.reshape(-1, 1)

    def _get_trainable_params(self):
        return 0

    def __call__(self, x):
        return self.W @ x
    
    def grads(self, dprev):
        return self.W.T @ dprev

    def _apply_grads(self, grads, lr):
        pass

    def __str__(self):
        return "Dropout : (keep_prob = %.1f)" % self.keep_prob