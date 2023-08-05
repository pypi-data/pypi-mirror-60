import tensorflow as tf, numpy as np

from typing import List
from neumf.model.layers import (
    MatrixFactorizationSlice, MultiLayerPerceptronSlice
)
from neumf.model.loss import (
    sigmoid_cross_entropy_with_logits,
)
from neumf.data.transform import scores_to_probabilities


class NeuMF:

    def __init__(self,
        num_users,
        num_items,
        num_factors:int=8,
        layers:List[int]=[64, 32, 16, 8],
        mf_regularization:float=0.,
        mlp_regularization:List[float]=[0., 0., 0., 0.],
        num_neg:int=4,
        learning_rate:float=0.001,
        beta1:float=0.9,
        beta2:float=0.999,
        epsilon:float=1e-8,
        hr_threshold:float=1.0,
        constructor_type:str='bisection',
        ml_perf:bool=False,
        early_stopping:bool=False
    ):
        '''
        Arguments:
            num_factors (int): the  embedding size of the Matrix Factorization
                model. Defaults to `8`.

            layers (int[]): The sizes of hidden layers for the Multi-Layer
                Perceptron. Defaults to `[64, 32, 16, 8]`.

            mf_regularization (float): The regularization factor for Matrix
                Factorization embedding. The factor is used by regularizer which
                allows to apply penalties on layer parametrs or layer activity
                during optimization.

            mlp_regularization (float[]): The regularization for each
                Multi-Layer Perceptron layer. Should match number of layers
                specified in `layers`. See `mf_regularization` for more info
                about regularization factors. Defaults to `[0., 0., 0., 0.]`.


            num_neg (int): the number of negative instances to pair with a
                positive instance.

            learning_rate (float): the learning rate.

            beta1 (float): beta1 hyperparameter for the Adam Optimizer.

            beta2 (float): beta2 hyperparameter for the Adam Optimizer.

            epsilon (float): epsilon hyperparameter for the Adam Optimizer.

            hr_threshold (float): If passed, training will stop when the
                evaluation metric HR is greater than or equal to hr_threshold.

            constructor_type (string): Strategy to use for generating false
                negatives. materialized has a precompute that scales badly, but
                a faster per-epoch construction time and can be faster on very
                large systems.

                Options: `bisection`, `materialized`.
                Default: `bisection`

            ml_perf (bool): If set, changes the behavior of the model slightly
                to match the MLPerf reference implementations here:
                    https://github.com/mlperf/reference/tree/master/recommendation/
                The two changes are:
                    1. When computing the HR and NDCG during evaluation, remove
                        duplicate user-item pairs before the computation.
                        This results in better HRs and NDCGs.
                    2. Use a different soring algorithm when sorting the input
                        data, which performs better due to the fact the sorting
                        algorithms are not stable.

        '''
        mf_dim = num_factors
        model_layers = list(map(int, layers))
        mlp_reg_layers = list(map(float, mlp_regularization))
        self.num_users = num_users
        self.num_items = num_items
        self.mf_dim = mf_dim # mf_dim
        self.model_layers = model_layers # model_layers
        self.mf_regularization = mf_regularization
        self.mlp_reg_layers = mlp_reg_layers
        self.num_neg = num_neg
        self.learning_rate = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.hr_threshold = hr_threshold
        self.constructor_type = constructor_type
        self.ml_perf = ml_perf
        self.early_stopping = early_stopping


        embedding_initializer = "glorot_uniform"
        self.embedding_user = tf.keras.layers.Embedding(
            num_users,
            mf_dim + model_layers[0] // 2,
            embeddings_initializer=embedding_initializer,
            embeddings_regularizer=tf.keras.regularizers.l2(mf_regularization),
            input_length=1,
            name="embedding_user"
        )
        self.embedding_item = tf.keras.layers.Embedding(
            num_items,
            mf_dim + model_layers[0] // 2,
            embeddings_initializer=embedding_initializer,
            embeddings_regularizer=tf.keras.regularizers.l2(mf_regularization),
            input_length=1,
            name="embedding_item"
        )


        self.mf_user_latent = MatrixFactorizationSlice(dim=mf_dim, name='embedding_user_mf')
        self.mf_item_latent = MatrixFactorizationSlice(dim=mf_dim, name='embedding_item_mf')

        self.mlp_user_latent = MultiLayerPerceptronSlice(dim=mf_dim, name='embedding_user_mlp')
        self.mlp_item_latent = MultiLayerPerceptronSlice(dim=mf_dim, name='embedding_item_mlp')

        mlp_layers = []
        for units, reg in zip(model_layers, mlp_reg_layers):
            dlayer = tf.keras.layers.Dense(
                units,
                kernel_regularizer=tf.keras.regularizers.l2(reg),
                activation="relu"
            )
            mlp_layers.append(dlayer)
        self.mlp_layers = mlp_layers


        self.logits = tf.keras.layers.Dense(
            1,
            activation=None,
            kernel_initializer="lecun_uniform",
            name='ratings'
        )
        self.model = None

        self.optimizer = tf.keras.optimizers.Adam(learning_rate, beta1, beta2, epsilon)
        self.loss = sigmoid_cross_entropy_with_logits
        pass


    def wire(
        self,
        user_input=None, item_input=None,
        user_shape=(1,), item_shape=(1,),
        verbose=False
    ):
        '''
        Constructs the model and sets it to self.model

        Arguments:
            user_input (tf.keras.Input): Defaults to None.
            item_input (tf.keras.Input): Defaults to None.
            user_shape (tuple): the shape of the user input. Defaults to `(1, )`.
            item_shape (tuple): the shape of the item input. Defaults to `(1, )`.
            verbose (bool): Defaults to False. Whether or not to print out model
                summary.

        Returns
            model (tf.keras.models.Model)
        '''
        input_u = user_input
        if input_u is None:
            input_u = tf.keras.Input(shape=user_shape)
        input_i = item_input
        if input_i is None:
            input_i = tf.keras.Input(shape=item_shape)

        emb_user = self.embedding_user(input_u)
        emb_item = self.embedding_item(input_i)

        # GMF part
        mf_lat_user = self.mf_user_latent(emb_user)
        mf_lat_item = self.mf_item_latent(emb_item)

        # MLP part
        mlp_lat_user = self.mlp_user_latent(emb_user)
        mlp_lat_item = self.mlp_item_latent(emb_item)

        # Element-wise multiply
        mf_vector = tf.keras.layers.multiply([mf_lat_user, mf_lat_item])

        # Concatenation of two latent features
        mlp_vector = tf.keras.layers.concatenate([mlp_lat_user, mlp_lat_item])

        # MLP
        for layer in self.mlp_layers:
            mlp_vector = layer(mlp_vector)

        # Concatenate GMF and MLP parts
        predict_vector = tf.keras.layers.concatenate([mf_vector, mlp_vector])

        # Final prediction layer
        logits = self.logits(predict_vector)

        model = tf.keras.models.Model([input_u, input_i], logits)
        if verbose:
            model.summary()
        self.model = model
        return model

    def compile(self):
        '''
        Compile the model with default optimizer and custom loss.
        '''
        # TODO: allow user to extend this
        self.model.compile(
            optimizer=self.optimizer,
            loss ={
                'ratings': self.loss
            },
            metrics=[
                tf.keras.metrics.Accuracy()
            ],
        )
        return self.model

    def get_mf_weights(self):
        '''
        Gets the latent factors for the user and items of the MF part
        '''
        w_u = self.model.get_layer('embedding_user').get_weights()[0]
        w_i = self.model.get_layer('embedding_item').get_weights()[0]
        return w_u[:, :self.mf_dim], w_i[:, :self.mf_dim]

    def get_mlp_weights(self):
        '''
        Gets the embedding factors for the user and items of the MLP part
        '''
        w_u = self.model.get_layer('embedding_user').get_weights()[0]
        w_i = self.model.get_layer('embedding_item').get_weights()[0]
        return w_u[:, self.mf_dim:], w_i[:, self.mf_dim:]

    def normalize_weights(self, weights):
        '''
        Normalize the given weights
        '''
        # normalize weights of MF so that their product is cosine similarity
        return weights / np.linalg.norm(weights, axis=1).reshape((-1,1))

    def _closest(self, idx, weights, n=10, least:bool=False, normalized:bool=False):
        '''
        Utility function for finding the n closes items / user to the given index
        of the provided item / user

        Arguments:
            idx (int): index of the element to find closest neighbors
            weights (list): the latent factors corresponding to the items / users
            n (int): how many results to return
            least (bool): whether or not to return the closest or farthest elements.
                Defaults to `False` (the closest).
            normalized (bool): Whether or not the weights are normalized.
                Defaults to `False` (weights will be normalized).
        '''
        if not normalized:
            w = self.normalize_weights(weights)
        else:
            w = weights
        # Calculate dot product between elem and all others
        dists = np.dot(w, w[idx]).clip(0)

        # Sort distance indexes from smallest to largest
        # cosine similarity so 0 is far and 1 is close
        sorted_dists = np.argsort(dists)
        closest = sorted_dists[:n] if least else np.flip(sorted_dists[-n:])

        return (dists, closest)

    def closest(self, idx, which='item', n=10, least:bool=False, ignore:list=[]):
        '''
        Finding the n closes items / user to the given index

        Arguments:
            idx (int): index of the element to find closest neighbors

            which (str): either `'item'` or `'user'`. Whether or not `idx`
                corresponds to items or users.

            n (int): how many results to return

            least (bool): whether or not to return the closest or farthest elements.
                Defaults to `False` (the closest).

            ignore (list): list of ids to ignore in recommendations. Defaults to `[]`.
        '''
        w_u, w_i = self.get_mf_weights()
        w = w_i if which == 'item' else w_u
        distances, closest = self._closest(idx, w, n, least, normalized=False)
        return [rec for rec in closest if rec not in ignore]

    def item_scores_for_user(self, idx:int):
        '''
        Calculate all `num_item` scores for the given user `idx`.
        Arguments:
            idx (int): the embedded index of the user.

        Returns:
            scores: raw logits of the model.
        '''
        scores = self.model.predict([
            np.ones(self.num_items, dtype=int) * idx,
            np.arange(self.num_items)
        ])
        return scores

    def items_for_user(self, idx, n=10, ignore:list=[]):
        '''
        Recommends n items for the given user
        Arguments:
            idx (int): the embedded index of the user.
            n (int): how many results to return
            ignore (list): list of ids to ignore in recommendations. Defaults to `[]`.
        Returns:
            recommendations: the top n recommendations (item ids) for the given
                user.
        '''
        scores = self.item_scores_for_user(idx)
        probs = scores_to_probabilities(scores)
        ranked = np.argsort(probs)
        ranked = [rec for rec in ranked if rec not in ignore]
        return np.flip(ranked[-n:])
