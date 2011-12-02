#!/usr/bin/python

from pyfann import libfann
import pickle
import numpy
import sys
import gzip
from pprint import pprint

# nacitame data set do pamate.
train_data_set = libfann.training_data()

train_input = []
train_output = []

num_input = 0
for f in sys.argv[1:]:
	with gzip.open(f, "r") as input_file:
		try:
			while True:
				velx, vely, out_values, time = pickle.load(input_file)
				

				train_input.append(list(velx.flatten()) + list(vely.flatten()))
				train_output.append(out_values)
		except EOFError:
			pass

num_input = len(train_input[0])
num_hidden1 = 64
num_output = len(train_output[0])

topology = (num_input, num_hidden1, num_output)

print len(train_input) , len(train_output)

train_data_set.set_train_data(train_input, train_output)

del train_input
del train_output

nn = libfann.neural_net()
pprint(topology)
nn.create_standard_array(topology)
nn.set_training_algorithm(libfann.TRAIN_RPROP)
nn.set_activation_function_output(libfann.SIGMOID_STEPWISE)

nn.train_on_data(train_data_set, 10000, 50, 0.01)

nn.save("test.net")
