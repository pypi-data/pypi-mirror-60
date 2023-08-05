import tensorflow as tf, numpy as np
from neumf.data.utils import shared_sort, numeric_breaks

class NegativeTransactionTable:
    '''
    Look up negative examples based on positive examples
    Notes:
        - memory intensive

    Arguments:
        users (list): the positive user examples
        items (list): the positive item examples
        num_users (int): the number of users
        num_items (int): the number of items
    '''
    def __init__(self, users, items, num_users, num_items):
        super(NegativeTransactionTable, self).__init__()
        self.users, self.items = shared_sort((users, items))
        self.num_users = num_users
        self.num_items = num_items

        self.negative_table = None
        self.per_user_neg_count = None

    def construct_table(self):
        index_bounds = numeric_breaks(self.users)
        negative_table = np.zeros(shape=(self.num_users, self.num_items), dtype=np.int32) - 1
        full_set = np.arange(self.num_items)
        per_user_neg_count = np.zeros(shape=(self.num_users,), dtype=np.int32)
        for i in range(self.num_users):
            positives = self.items[index_bounds[i]:index_bounds[i+1]]
            negatives = np.delete(full_set, positives)
            per_user_neg_count[i] = self.num_items - positives.shape[0]
            negative_table[i, :per_user_neg_count[i]] = negatives

        self.negative_table = negative_table
        self.per_user_neg_count = per_user_neg_count
        return negative_table

    def lookup_negative_items(self, users, **kwargs):
        neg_choices = [
            np.random.randint(self.per_user_neg_count[user])
            for user in users
        ]
        return self.negative_table[users, neg_choices]
