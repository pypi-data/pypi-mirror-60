from littlenn.activation_functions.abstract_activation import ActivationFunction

class ReLU(ActivationFunction):
    def __call__(self, x):
        return np.maximum(x, 0)
    def derivative(self, x):
        return np.maximum(x / np.abs(x + 1e-12), 0)