import tensorflow as tf, numpy as np
import os, math

from neumf.data.NegativeTransactionTable import NegativeTransactionTable
from neumf.data.utils import shared_shuffle, batch_idx

class TransactionSequence(tf.keras.utils.Sequence):
    def __init__(
        self, users, items, num_users, num_items,
        batch_size=32, neg_ratio=4, pad_last=True
    ):
        '''
        A custom tf.keras.utils.Sequence for transaction data.
        Notes:
            - depends on `NegativeTransactionTable`
            - batch size will be `batch_size * (1+neg_ratio)`

        Arguments:
            users (list): the positive user examples
            items (list): the positive item examples
            num_users (int): the number of users
            num_items (int): the number of items
            batch_size (int): how many positive examples to include in the model
            neg_ratio (int): how many negative examples, per positive example to
                include in a batch.
            pad_last (bool): Whether or not to pad the last batch or drop it.

        '''
        self.num_users = num_users
        self.num_items = num_items
        self.batch_size = batch_size
        self.adjusted_batch_size = batch_size * (neg_ratio+1)
        self.neg_ratio = neg_ratio
        self.pad_last = pad_last

        neg_table = NegativeTransactionTable(users, items, num_users, num_items)
        neg_table.construct_table()
        self.neg_table = neg_table

        self.users, self.items = shared_shuffle((users, items))

    def on_epoch_end(self):
        '''
        Update positive examples order
        '''
        self.users, self.items = shared_shuffle((self.users, self.items))


    def __len__(self):
        '''
        How many batches in the sequence
        '''
        d = len(self.items) / self.batch_size
        if self.pad_last:
            return math.ceil(d)
        return math.floor(d)

    def __getitem__(self, idx):
        a, b = batch_idx(idx, self.batch_size)
        b_users = self.users[a:b]
        b_items = self.items[a:b]
        b_pos = np.ones_like(b_users)

        n_users = np.repeat(b_users, self.neg_ratio)
        n_items = self.neg_table.lookup_negative_items(n_users)
        b_neg = np.zeros_like(n_users)

        b_u = np.concatenate((b_users, n_users))
        b_i = np.concatenate((b_items, n_items))
        b_y = np.concatenate((b_pos, b_neg))

        # need to pad, will do so evenly with random _previously_ seen positive and negative examples
        if self.adjusted_batch_size > len(b_u):
            diff = self.adjusted_batch_size - len(b_u)
            pad_neg = round(diff / 2)
            pad_pos = diff-pad_neg

            ppu = np.random.choice(np.arange(len(self.users)), pad_pos)
            b_u = np.concatenate((
                b_u,
                self.users[ppu],
                self.users[ppu][:pad_neg]
            ))
            b_i = np.concatenate((
                b_i,
                self.items[ppu],
                self.neg_table.lookup_negative_items(self.users[ppu])[:pad_neg]
            ))
            b_y = np.concatenate((b_y, np.ones_like(ppu), np.zeros((pad_neg))))


        b = np.array([b_u, b_i, b_y])


        i = np.arange(self.adjusted_batch_size)
        np.random.shuffle(i)
        x, y = tuple(b[:2, i]), b[2:, i].reshape(-1)
        return x, y
