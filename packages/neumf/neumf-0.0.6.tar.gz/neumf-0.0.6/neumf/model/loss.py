import tensorflow as tf, numpy as np
from neumf.data.transform import convert_to_softmax_logits

# softmax_sparse_softmax_cross_entropy_with_logits
def sigmoid_cross_entropy_with_logits(labels, logits):
    '''
    Custom loss for GNMF model.

    First calculates appends zeros to each example so that the softmax of the
    logits is equivalent to the sigmoid. Then applies cross entory loss.

    Arguments
        labels (list): the labels for each examples (shape (-1, 1))
        logits (list): the output of the model for each example.

    '''
    softmax_logits = convert_to_softmax_logits(logits)

    loss = tf.nn.softmax_cross_entropy_with_logits(
        labels=labels,
        logits=softmax_logits
    )

    return loss
