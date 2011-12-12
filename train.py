#!/usr/bin/python

from pyfann import libfann
import pickle
import numpy
import sys
import gzip
from pprint import pprint

from vision  import *

# nacitame data set do pamate.
train_data_set = libfann.training_data()

train_input = []
train_output = []

num_input = 0
for f in sys.argv[1:]:
	with gzip.open(f, "r") as input_file:
		try:
			while True:
				in_values, out_values = pickle.load(input_file)

				train_input.append(in_values)
				train_output.append(out_values)

				mirror_in_values = mirror_motion_vector(in_values)
				mirror_out_values = (out_values[0], -out_values[1])

				train_input.append(mirror_in_values)
				train_output.append(mirror_out_values)
		except EOFError:
			pass


topology = (len(train_input[0]), 32, len(train_output[0]))

print len(train_input) , len(train_output)

train_data_set.set_train_data(train_input, train_output)

del train_input
del train_output

nn = libfann.neural_net()
pprint(topology)
nn.create_standard_array(topology)
nn.set_learning_rate(0.3)
#nn.set_training_algorithm(libfann.TRAIN_RPROP)
#nn.set_training_algorithm(libfann.TRAIN_INCREMENTAL)
nn.set_training_algorithm(libfann.TRAIN_QUICKPROP)
#nn.set_training_algorithm(libfann.TRAIN_BATCH)
#nn.set_activation_function_output(libfann.LINEAR)
#nn.set_activation_function_output(libfann.SIGMOID_SYMMETRIC)
nn.set_activation_function_output(libfann.GAUSSIAN_SYMMETRIC)
#nn.set_activation_function_output(libfann.SIGMOID)
nn.set_train_stop_function(libfann.STOPFUNC_MSE)

nn.train_on_data(train_data_set, 20000, 1000, 0.007)

nn.save("test.net")
