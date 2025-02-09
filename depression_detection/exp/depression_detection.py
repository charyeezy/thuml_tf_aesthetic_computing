# Hint: you should refer to the API in https://github.com/tensorflow/tensorflow/tree/r1.0/tensorflow/contrib
# Use print(xxx) instead of print xxx
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import numpy as np
import shutil
import os
from sklearn.model_selection import train_test_split


# Global config, please don't modify
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
config.gpu_options.per_process_gpu_memory_fraction = 0.20
sess = tf.Session(config=config)
model_dir = r'../model'

# Dataset location
DEPRESSION_DATASET = '../data/data.csv'
DEPRESSION_TRAIN = '../data/training_data.csv'
DEPRESSION_TEST = '../data/testing_data.csv'

# Delete the exist model directory
if os.path.exists(model_dir):
    shutil.rmtree(model_dir)



# TODO: 1. Split data (5%)
'''
data = np.loadtxt(DEPRESSION_DATASET, delimiter=',')
data_X = data[:,:-1]
data_y = data[:,-1]
X_train, X_test, y_train, y_test = train_test_split(data_X, data_y, test_size=0.4)
'''

# Split data: split file DEPRESSION_DATASET into DEPRESSION_TRAIN and DEPRESSION_TEST with a ratio about 0.6:0.4.
# Hint: first read DEPRESSION_DATASET, then output each line to DEPRESSION_TRAIN or DEPRESSION_TEST by use
# random.random() to get a random real number between 0 and 1.


# TODO: 2. Load data (5%)

training_set = tf.contrib.learn.datasets.base.load_csv_without_header(
    filename=DEPRESSION_TRAIN,
    target_dtype=np.int8,
    features_dtype=np.float32)

test_set = tf.contrib.learn.datasets.base.load_csv_without_header(
    filename=DEPRESSION_TEST,
    target_dtype=np.int8,
    features_dtype=np.float32)

features_train = tf.constant(training_set.data)
features_test = tf.constant(test_set.data)
labels_train = tf.constant(training_set.target)
labels_test = tf.constant(test_set.target)

# TODO: 3. Normalize data (15%)
data_cat = tf.concat([features_train, features_test], axis=0)
data_norm = tf.nn.l2_normalize(data_cat, axis=0)
features_train_norm = data_norm[0:features_train.shape[0]]
features_test_norm = data_norm[features_train.shape[0]:features_train.shape[0] + features_test.shape[0]]

# Hint:
# we must normalize all the data at the same time, so we should combine the training set and testing set
# firstly, and split them apart after normalization. After this step, your features_train and features_test will be
# new feature tensors.
# Some functions you may need: tf.nn.l2_normalize, tf.concat, tf.slice

# TODO: 4. Build linear classifier with `tf.contrib.learn` (5%)

dim = int(features_train.shape[1]) 
feature_columns = [tf.contrib.layers.real_valued_column("", dimension=dim)]

# You should fill in the argument of LinearClassifier
#classifier = tf.contrib.learn.LinearClassifier(model_dir=model_dir, n_classes=2, feature_columns=feature_columns)

# TODO: 5. Build DNN classifier with `tf.contrib.learn` (5%)

# You should fill in the argument of DNNClassifier
classifier = tf.contrib.learn.DNNClassifier(model_dir=model_dir, hidden_units=[128, 64], optimizer=tf.train.AdamOptimizer(learning_rate=0.001), feature_columns=feature_columns)

# Define the training inputs
def get_train_inputs():
    x = tf.constant(features_train_norm.eval(session=sess))
    y = tf.constant(labels_train.eval(session=sess))

    return x, y

# Define the test inputs
def get_test_inputs():
    x = tf.constant(features_test_norm.eval(session=sess))
    y = tf.constant(labels_test.eval(session=sess))

    return x, y

# TODO: 6. Fit model. (5%)
classifier.fit(input_fn=get_train_inputs, steps=400)




validation_metrics = {
    "true_negatives":
        tf.contrib.learn.MetricSpec(
            metric_fn=tf.contrib.metrics.streaming_true_negatives,
            prediction_key=tf.contrib.learn.PredictionKey.CLASSES
        ),
    "true_positives":
        tf.contrib.learn.MetricSpec(
            metric_fn=tf.contrib.metrics.streaming_true_positives,
            prediction_key=tf.contrib.learn.PredictionKey.CLASSES
        ),
    "false_negatives":
        tf.contrib.learn.MetricSpec(
            metric_fn=tf.contrib.metrics.streaming_false_negatives,
            prediction_key=tf.contrib.learn.PredictionKey.CLASSES
        ),
    "false_positives":
        tf.contrib.learn.MetricSpec(
            metric_fn=tf.contrib.metrics.streaming_false_positives,
            prediction_key=tf.contrib.learn.PredictionKey.CLASSES
        ),
}

# TODO: 7. Make Evaluation (10%)

# evaluate the model and get TN, FN, TP, FP
result = classifier.evaluate(input_fn=get_test_inputs, steps=400, metrics=validation_metrics)


TN = result["true_negatives"]
FN = result["false_negatives"]
TP = result["true_positives"]
FP = result["false_positives"]

# You should evaluate your model in following metrics and print the result:
# Accuracy
accuracy = (TP + TN) / (TP + TN + FP + FN)

# Precision in macro-average
precision = (TP / (TP + FP) + TN / (TN + FN)) / 2

# Recall in macro-average
recall = (TP / (TP + FN) + TN / (TN + FP)) / 2

# F1-score in macro-average
F1 = 2 * recall * precision / (recall + precision)

# Print
print("Results:")
print("accuracy:  ", str(accuracy))
print("precision: ", str(precision))
print("recall:    ", str(recall))
print("F1:        ", str(F1))