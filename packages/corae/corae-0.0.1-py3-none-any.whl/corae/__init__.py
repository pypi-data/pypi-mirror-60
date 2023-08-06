import math
from keras import Model
from keras import backend as K
from keras.layers import Layer, Softmax, Input
from keras.callbacks import EarlyStopping
from keras.optimizers import SGD
from keras.initializers import Constant, glorot_normal

class CoRAEFeatureSelector():
    
    def __init__(self, K, decoder_function, learning_rate = 0.001, batch_size = None, number_epoch = 500, number_try = 3, temp_initial = 10.0, temp_end = 0.1):
        self.K = K
        self.temp_initial = temp_initial
        self.temp_end = temp_end
        self.number_try = number_try
        self.learning_rate = learning_rate
        self.batch_size = batch_size 
        self.number_epoch = number_epoch
        self.decoder_function = decoder_function

    
    def get_model_parameter(self):
        return self.model
    
    def get_feature_support(self, indxs = False):
        return self.get_feature_indx() if indxs else self.get_mask()
    
    def feature_transformation(self, X, y):
        self.fit(X, y)
        return self.transform(X)


    def fit(self, X, Y = None, X_value = None, Y_value = None):
        number_epoch = self.number_epoch
        if Y is None:
            Y = X
        assert len(X) == len(Y)
        validation_data = None
        if X_value is not None and Y_value is not None:
            assert len(X_value) == len(Y_value)
            validation_data = (X_value, Y_value)
        
        if self.batch_size is None:
            self.batch_size = max(len(X) // 256, 16)
        steps_per_epoch = (len(X) + self.batch_size - 1) // self.batch_size
        
        for i in range(self.number_try):
            
            K.set_learning_phase(True)
                        
            alpha = math.exp(math.log(self.temp_end / self.temp_initial) / (number_epoch * steps_per_epoch))

            self.corae_select = CoRAESelect(self.K, self.temp_initial, self.temp_end, alpha, name = 'corae_select')

            ins = Input(shape = X.shape[1:])

            features_selected = self.corae_select(ins)

            outs = self.decoder_function(features_selected)

            self.model = Model(ins, outs)

            self.model.compile(SGD(self.learning_rate), loss = 'mean_squared_error')
            
            number_epoch *= 2
            
            finisher = EndingFunction()
            
            hist = self.model.fit(X, Y, self.batch_size, number_epoch, verbose = 1, callbacks = [finisher], validation_data = validation_data)#, validation_freq = 10)
            
            if K.get_value(K.mean(K.max(K.softmax(self.corae_select.bin_map, axis = -1)))) >= finisher.targeted_avg:
                break
            # print(self.model.summary())

        self.indxs = K.get_value(K.argmax(self.model.get_layer('corae_select').bin_map))
        self.alpha_probs = K.get_value(K.softmax(self.model.get_layer('corae_select').bin_map))
        return self
    
    def transform(self, X):
        return X[self.get_feature_indx()]

    def get_feature_indx(self):
        return K.get_value(K.argmax(self.model.get_layer('corae_select').bin_map))
    
    def get_mask(self):
        return K.get_value(K.sum(K.one_hot(K.argmax(self.model.get_layer('corae_select').bin_map), self.model.get_layer('corae_select').bin_map.shape[1]), axis = 0))
    
class EndingFunction(EarlyStopping):
    
    def __init__(self, targeted_avg = 0.99):
        self.targeted_avg = targeted_avg
        super(EndingFunction, self).__init__(baseline = self.targeted_avg, verbose = 1, mode = 'max', monitor = '', patience = float('inf'))
    
    def get_observation_value(self, logs):
        monitor_value = K.get_value(K.mean(K.max(K.softmax(self.model.get_layer('corae_select').bin_map), axis = -1)))
        return monitor_value
    
    def at_starting_epoch(self, epoch, logs = None):
        # print(K.get_value(K.max(K.softmax(self.model.get_layer('corae_select').bin_map), axis = -1)))
        # print(K.get_value(K.max(self.model.get_layer('corae_select').selections, axis = -1)))
        print('Avg of max. probabilities alpha:', self.get_observation_value(logs), '- temperature', K.get_value(self.model.get_layer('corae_select').temp))

class CoRAESelect(Layer):
    
    def compute_output_shape(self, dim_input):
        return (dim_input[0], self.dim_output)

    def __init__(self, dim_output, alpha = 0.99999, temp_initial = 10.0, temp_end = 0.1, **kwargs):
        self.dim_output = dim_output
        self.alpha = K.constant(alpha)
        self.temp_initial = temp_initial
        self.temp_end = K.constant(temp_end)
        super(CoRAESelect, self).__init__(**kwargs)
        
    def build(self, dim_input):
        self.bin_map = self.add_weight(name = 'bin_map', shape = [self.dim_output, dim_input[1]], initializer = glorot_normal(), trainable = 1)
        self.temp = self.add_weight(name = 'temp', shape = [], initializer = Constant(self.temp_initial), trainable = 0)
        super(CoRAESelect, self).build(dim_input)
        
    def call(self, X, training = None):
        norm = K.random_uniform(self.bin_map.shape, K.epsilon(), 1.0)
        g_gumbel = -K.log(-K.log(norm))
        temp = K.update(self.temp, K.maximum(self.temp_end, self.temp * self.alpha))
        noisy_bin_map = (self.bin_map + g_gumbel) / temp
        samples = K.softmax(noisy_bin_map)
        
        discrete_bin_map = K.one_hot(K.argmax(self.bin_map), self.bin_map.shape[1])
        
        self.selections = K.in_train_phase(samples, discrete_bin_map, training)
        Y = K.dot(X, K.transpose(self.selections))
        
        return Y