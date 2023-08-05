import tensorflow as tf, numpy as np
from scipy.special import softmax

def to_int_feature(values):
    '''Converts list of ints to tf.Train.Feature'''
    return tf.train.Feature(int64_list=tf.train.Int64List(value=list(values)))

def serialize_transaction_data(data:dict):
    '''
    Converts dict of key, value pairs, where each value is a list of integers
    to a `tf.train.Example`
    '''
    features = {
        k: to_int_feature(v.astype(np.int64))
        for k, v in data.items()
        if type(v) is list
    }
    return tf.train.Example(features=tf.train.Features(feature=features)).SerializeToString()

def convert_to_softmax_logits(logits:list)->list:
  '''
  Convert the logits returned by the base model to softmax logits.

  Arguments:
    logits: used to create softmax.

  Returns:
    Softmax with the first column of zeros is equivalent to sigmoid.
  '''
  softmax_logits = tf.concat([logits * 0, logits], axis=1)
  return softmax_logits

def scores_to_probabilities(scores:list):
    '''
    Converts raw scores to probabilities.

    Arguments:
        scores (list): the raw logits (scores) of the model.

    Returns
        probabilities (list)
    '''
    softmax_logits = np.concatenate([scores * 0, scores], axis=1)
    return softmax(softmax_logits, axis=-1).round(5)[:, 1]
