#!/usr/bin/python

from pyfann import libfann
import pickle
import numpy
import sys
import gzip
import time
from pprint import pprint

from vision  import *

ph_corr = 4
mirror = True

# nacitame data set do pamate.
train_data_set = libfann.training_data()

train_input = []
train_output = []

num_input = 0
for f in sys.argv[1:]:
	with gzip.open(f, "r") as input_file:
		tmp_input = []
		tmp_output = []
		try:
			while True:
				in_values, out_values = pickle.load(input_file)

				tmp_input.append(in_values)
				tmp_output.append(out_values)

		except EOFError:
			pass

# phase correction
		if len(tmp_input) < ph_corr:
			continue

		if ph_corr < 0:
			tmp_input = tmp_input[:ph_corr]
			tmp_output = tmp_output[-ph_corr:]
		if ph_corr > 0:
			tmp_input = tmp_input[ph_corr:]
			tmp_output = tmp_output[:-ph_corr]

		if mirror:
			mirror_input = [mirror_motion_vector(x) for x in tmp_input]
			mirror_output = [(x[0], -x[1]) for x in tmp_output]

			train_input = train_input + mirror_input
			train_output = train_output + mirror_output

		train_input = train_input + tmp_input
		train_output = train_output + tmp_output


print len(train_input) , len(train_output)
topology = (len(train_input[0]), 32, len(train_output[0]))


train_data_set.set_train_data(train_input, train_output)

del train_input
del train_output

nn = libfann.neural_net()
pprint(topology)
nn.create_standard_array(topology)
nn.set_learning_rate(0.2)
#nn.set_training_algorithm(libfann.TRAIN_RPROP)
#nn.set_training_algorithm(libfann.TRAIN_INCREMENTAL)
nn.set_training_algorithm(libfann.TRAIN_QUICKPROP)
#nn.set_training_algorithm(libfann.TRAIN_BATCH)
#nn.set_activation_function_output(libfann.LINEAR)
#nn.set_activation_function_output(libfann.SIGMOID_SYMMETRIC)
nn.set_activation_function_output(libfann.GAUSSIAN_SYMMETRIC)
#nn.set_activation_function_output(libfann.SIGMOID)
nn.set_train_stop_function(libfann.STOPFUNC_MSE)

nn.train_on_data(train_data_set, 20000, 1000, 0.003)

filename = "nn_" + time.strftime("%Y%m%d_%H%M%S") + ".net"
nn.save(filename)
print "network saved as: " + filename
