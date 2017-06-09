import tensorflow as tf
import summarizer
import os
import numpy as np
from tensorflow.examples.tutorials.mnist import input_data

IMAGE_SIZE = 28
NUM_CHANNELS = 1
NUM_LABELS = 10
SEED = 66478
BATCH_SIZE = 64

FLAGS = tf.app.flags.FLAGS

tf.app.flags.DEFINE_string('path', "/tmp/embed", "path")

if not os.path.exists(FLAGS.path):
    os.makedirs(FLAGS.path)

input_placeholder = tf.placeholder(tf.float32, shape=(BATCH_SIZE, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS))

conv1_weights = tf.Variable(tf.truncated_normal([5, 5, NUM_CHANNELS, 32], stddev=0.1, seed=SEED, dtype=tf.float32),
                            name='conv1_weights')
conv1_biases = tf.Variable(tf.zeros([32], dtype=tf.float32), name='conv1_biases')
conv2_weights = tf.Variable(tf.truncated_normal([5, 5, 32, 64], stddev=0.1, seed=SEED, dtype=tf.float32),
                            name='conv2_weights')
conv2_biases = tf.Variable(tf.constant(0.1, shape=[64], dtype=tf.float32), name='conv2_biases')
fc1_weights = tf.Variable(
    tf.truncated_normal([IMAGE_SIZE // 4 * IMAGE_SIZE // 4 * 64, 512], stddev=0.1, seed=SEED, dtype=tf.float32),
    name='fc1_weights')
fc1_biases = tf.Variable(tf.constant(0.1, shape=[512], dtype=tf.float32), name='fc1_biases')
fc2_weights = tf.Variable(tf.truncated_normal([512, NUM_LABELS], stddev=0.1, seed=SEED, dtype=tf.float32),
                          name='fc2_weights')
fc2_biases = tf.Variable(tf.constant(0.1, shape=[NUM_LABELS], dtype=tf.float32), name='fc2_biases')


def model(data):
    conv = tf.nn.conv2d(data, conv1_weights, strides=[1, 1, 1, 1], padding='SAME', name='conv1')
    relu = tf.nn.relu(tf.nn.bias_add(conv, conv1_biases), name='relu1')
    pool = tf.nn.max_pool(relu, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME', name='pool1')
    conv = tf.nn.conv2d(pool, conv2_weights, strides=[1, 1, 1, 1], padding='SAME', name='conv2')
    relu = tf.nn.relu(tf.nn.bias_add(conv, conv2_biases), name='relu2')
    pool = tf.nn.max_pool(relu, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME', name='pool2')
    pool_shape = pool.get_shape().as_list()
    reshape = tf.reshape(pool, [pool_shape[0], pool_shape[1] * pool_shape[2] * pool_shape[3]], name='reshape')
    hidden = tf.nn.relu(tf.matmul(reshape, fc1_weights) + fc1_biases, name='relu3')

    return tf.matmul(hidden, fc2_weights, name='matmul') + fc2_biases, conv


data_sets = input_data.read_data_sets(FLAGS.path, validation_size=BATCH_SIZE)

sess = tf.Session()
sess.run(tf.global_variables_initializer())

saver = tf.train.Saver()
saver.restore(sess, FLAGS.path)

logits, conv_layer = model(input_placeholder)
batch_dataset, batch_labels = data_sets.validation.next_batch(BATCH_SIZE)
batch_dataset = batch_dataset.reshape((-1, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS)).astype(np.float32)

summarizer.summary_embedding_with_labels(sess, batch_dataset, batch_labels, [conv_layer], input_placeholder, FLAGS.path,
                                         IMAGE_SIZE, NUM_CHANNELS, BATCH_SIZE)
