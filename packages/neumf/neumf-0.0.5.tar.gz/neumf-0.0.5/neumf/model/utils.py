import tensorflow as tf, numpy as np
import pickle
from neumf.model.layers import MatrixFactorizationSlice, MultiLayerPerceptronSlice
from neumf.model.loss import sigmoid_cross_entropy_with_logits
from neumf.model.NeuMF import NeuMF

CUSTOM_OBJECTS = {
    'MatrixFactorizationSlice': MatrixFactorizationSlice,
    'MultiLayerPerceptronSlice': MultiLayerPerceptronSlice,
    'sigmoid_cross_entropy_with_logits': sigmoid_cross_entropy_with_logits,
    'ratings': sigmoid_cross_entropy_with_logits,
}


def load_model(model_file:str, overview_file:str, num_factors:int=8)->dict:
    '''
    Arguments:
        model_file (str): fullpath to the h5 format saved model
        overview_file (str): fullpath to the pickle file generated from the data
            preprocessing pipeline function
            (`mkm.data.pipelines.preprocess_transaction_dataframe`). This is
            needed to know the number of items and users to initalize the
            `GNMF` class.
        num_factors (int): number of factors specified when training the saved model.
            Defaults to (8)

    Returns:
        model (neumf.model.NeuMF)
        overview (dict)

    '''
    with open(overview_file, 'rb') as f:
        overview = pickle.load(f)
    _model = tf.keras.models.load_model(model_file, CUSTOM_OBJECTS)
    model = NeuMF(overview['num_users'], overview['num_items'], num_factors=num_factors)
    model.model = _model
    return model, overview
