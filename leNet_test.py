import tensorflow as tf
import ops
import numpy as np
from tensorflow.examples.tutorials.mnist import input_data

mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
batch_size = 128
Train_steps = 10000
def add_full_layer(input_x,layer_numble,node_num,alpha = 1,activation_function = None):
	layer_name = 'full_connected_layer%s' %layer_numble
	with tf.name_scope(layer_name):
		with tf.name_scope('Weight'):
			Weight = tf.Variable(tf.random_normal([input_x.shape.as_list()[1]]+[node_num],stddev=0.1),trainable = False,dtype = tf.float32,name = "W")
			tf.summary.histogram(layer_name+'/Weight',Weight)
		with tf.name_scope('Bias'):
			bias = tf.Variable(tf.constant(0.1,shape = [node_num]),trainable = False,dtype = tf.float32,name = "b")
			tf.summary.histogram(layer_name+'/bias',bias)
		with tf.name_scope('W_x_add_b'):
			temp = tf.add(tf.matmul(input_x,alpha*Weight),bias)
		if(activation_function is None):
			output_y = temp
		else:
			output_y = activation_function(temp)
		tf.summary.histogram(layer_name+'/output',output_y)
		return output_y

# def comput_alpha(input_line,steps):
	# output = []
	# threshhold = comput_threshhold(input_line,steps)
	# sum1 = 0
	# sum2 = 0
	# for y in input_line:
		# if(y > threshhold):
			# sum1 += y
			# sum2 += 1 
			# y = 1.0
		# else:
			# y = 0.0
		# output.append(y)
	# alpha = sum1/sum2
	# return output,alpha

# def comput_threshhold(input_line,steps):
	# t = 1/steps
	# threshhold = 0
	# f_max = 0
	# threshhold_max = 0
	# for i in range(steps):
		# sum1 = 0
		# sum2 = 0
		# for y in input_line:
			# if(y > threshhold):
				# sum1 += y
				# sum2 += 1
		# if((pow(sum1,2)/sum2)>f_max):
			# threshhold_max = threshhold
			# f_max = (pow(sum1,2)/sum2)
		# threshhold += t
	# return threshhold_max
def comput_threshold(input_d,steps):
	threshhold = tf.constant(0.01)
	f_max = tf.constant(0.01)
	threshhold_max = tf.constant(0.01)
	for i in range(steps):
		output = tf.where(tf.greater(input_d,threshhold),tf.ones_like(input_d,tf.float32),tf.zeros_like(input_d,tf.float32))
		alpha_temp = tf.where(tf.greater(input_d,threshhold),tf.abs(input_d),tf.zeros_like(input_d,tf.float32))
		threshhold += 2/steps
		f_max_new = tf.square(tf.reduce_sum(alpha_temp))/tf.reduce_sum(output)
		threshhold_max = tf.where(tf.greater(f_max_new,f_max),threshhold,threshhold_max)
		f_max = tf.where(tf.greater(f_max_new,f_max),f_max_new,f_max)
	return threshhold_max

def add_2_binary(input_d,steps):
	threshhold = comput_threshold(input_d,steps)
	output = tf.where(tf.greater(input_d,threshhold),tf.ones_like(input_d,tf.float32),tf.zeros_like(input_d,tf.float32))
	alpha_temp = tf.where(tf.greater(input_d,threshhold),tf.abs(input_d),tf.zeros_like(input_d,tf.float32))
	alpha = tf.reduce_sum(alpha_temp)/tf.reduce_sum(output)
	return output,alpha,threshhold

def add_2_binary_op(input_d,threshhold):
	output = tf.where(tf.greater(input_d,threshhold),tf.ones_like(input_d,tf.float32),tf.zeros_like(input_d,tf.float32))
	return output

def add_cov_layer(input_x,layer_numble,filter_size,activation_function = None):
	layer_name = "convolutional_layer%s" %layer_numble
	with tf.name_scope(layer_name):
		with tf.name_scope("Filter"):
			Filter = tf.Variable(tf.random_normal(filter_size,stddev=0.1),dtype = tf.float32,name = "filter")
			tf.summary.histogram(layer_name+'/filter',Filter)
		with tf.name_scope("Bias"):
			bias = tf.Variable(tf.constant(0.1,shape = [filter_size[3]]),dtype = tf.float32,name = "bias")
			tf.summary.histogram(layer_name+'/bias',bias)
		with tf.name_scope("convolution"):
			conv = tf.nn.conv2d(input_x,Filter,strides=[1, 1, 1, 1], padding='VALID')
		with tf.name_scope('conv_add_b'):
			temp = tf.add(conv,bias)
		if(activation_function is None):
			output_y = temp
		else:
			output_y = activation_function(temp)
		tf.summary.histogram(layer_name+'/output',output_y)
		return output_y

def add_max_pool(input_x,layer_numble,k_size):
	layer_name = 'pool_layer%s' %layer_numble
	with tf.name_scope(layer_name):
		output_y = tf.nn.max_pool(input_x,k_size,strides=[1, 2, 2, 1],padding = 'VALID')
		tf.summary.histogram(layer_name+'/output',output_y)
	return output_y

def stack2line(input_x,layer_numble):
	layer_name = 'stack2line%s' %layer_numble
	with tf.name_scope(layer_name):
		output_y = tf.reshape(input_x,[-1,tf.cast(input_x.shape[1]*input_x.shape[2]*input_x.shape[3],tf.int32)])
	return output_y
########################################################
#the entrence of the data
with tf.device('/cpu:0'):
	with tf.name_scope('input'):
		x = tf.placeholder(tf.float32,[None,784],name = 'x_input')
		y_ = tf.placeholder(tf.float32,[None,10],name = 'y_input')
		x_imgs = tf.reshape(x,[-1,28,28,1])

keep_prob = tf.placeholder(tf.float32)
########################################################

########################################################
#the structure of the cnn:
with tf.device('/cpu:0'):
	input_x = add_2_binary_op(x_imgs,0.5)
	layer1 = add_cov_layer(input_x,1,[5,5,1,10],activation_function = tf.nn.relu)
	layer2 = add_max_pool(layer1,2,[1,2,2,1])
	layer3 = stack2line(layer2,3)
	alpha_1 = 0.98
	threshhold_1 = 0.61
	layer3_b = add_2_binary_op(layer3,threshhold_1)
	#layer3_b,alpha_1,threshhold_1 = add_2_binary(layer3,100)
	layer4 = add_full_layer(layer3_b,4,400,alpha_1,activation_function = tf.nn.relu)
	layer4_drop = tf.nn.dropout(layer4,keep_prob)
	alpha_2 = 3.3
	threshhold_2 = 1.63
	layer4_b = add_2_binary_op(layer4_drop,threshhold_2)
	# layer4_b,alpha_2,threshhold_2 = add_2_binary(layer4_drop,100)
	layer5 = add_full_layer(layer4_b,5,60,alpha_2,activation_function = tf.nn.relu)
	layer5_drop = tf.nn.dropout(layer5,keep_prob)
	y = add_full_layer(layer5_drop,6,10,activation_function =tf.nn.softmax)
#########################################################

#########################################################
#culculate the accuracy
with tf.device('/cpu:0'):
	with tf.name_scope('accuracy'):
		prediction = tf.equal(tf.argmax(y,1),tf.argmax(y_,1))
		accuracy = tf.reduce_mean(tf.cast(prediction,tf.float32),name = 'accuracy')
		tf.summary.scalar('accuracy',accuracy)
#########################################################

save=tf.train.Saver()

with tf.Session(config = tf.ConfigProto(log_device_placement = True)) as sess:
	init = tf.global_variables_initializer()
	sess.run(init)
	save.restore(sess,'net_data/le_net/cnn_theta.ckpt')
	accuracy_test_train = sess.run(accuracy,feed_dict = {x:mnist.test.images,y_:mnist.test.labels,keep_prob:1.0})
	# threshhold_layer1_train = sess.run(threshhold_1,feed_dict = {x:mnist.test.images,y_:mnist.test.labels,keep_prob:1.0})
	# alpha_layer1_train = sess.run(alpha_1,feed_dict = {x:mnist.test.images,y_:mnist.test.labels,keep_prob:1.0})
	# threshhold_layer2_train = sess.run(threshhold_2,feed_dict = {x:mnist.test.images,y_:mnist.test.labels,keep_prob:1.0})
	# alpha_layer2_train = sess.run(alpha_2,feed_dict = {x:mnist.test.images,y_:mnist.test.labels,keep_prob:1.0})
with tf.Session(config = tf.ConfigProto(log_device_placement = True)) as sess:
	init = tf.global_variables_initializer()
	sess.run(init)
	save.restore(sess,'net_data/le_net_9881/cnn_theta.ckpt')
	accuracy_test_original = sess.run(accuracy,feed_dict = {x:mnist.test.images,y_:mnist.test.labels,keep_prob:1.0})
	# threshhold_layer1 = sess.run(threshhold_1,feed_dict = {x:mnist.test.images,y_:mnist.test.labels,keep_prob:1.0})
	# alpha_layer1 = sess.run(alpha_1,feed_dict = {x:mnist.test.images,y_:mnist.test.labels,keep_prob:1.0})
	# threshhold_layer2 = sess.run(threshhold_2,feed_dict = {x:mnist.test.images,y_:mnist.test.labels,keep_prob:1.0})
	# alpha_layer2 = sess.run(alpha_2,feed_dict = {x:mnist.test.images,y_:mnist.test.labels,keep_prob:1.0})
	print('the original accuracy on test data is %g'%(accuracy_test_original))
	# print('the threshhold_1 is %g , the alpha_1 is %g'%(threshhold_layer1,alpha_layer1))
	# print('the threshhold_2 is %g , the alpha_2 is %g'%(threshhold_layer2,alpha_layer2))
	print('the train accuracy on test data is %g'%(accuracy_test_train))
	# print('the threshhold_1 is %g , the alpha_1 is %g'%(threshhold_layer1_train,alpha_layer1_train))
	# print('the threshhold_2 is %g , the alpha_2 is %g'%(threshhold_layer2_train,alpha_layer2_train))
	