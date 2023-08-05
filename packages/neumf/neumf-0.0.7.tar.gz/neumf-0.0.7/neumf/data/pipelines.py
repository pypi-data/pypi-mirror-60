import tensorflow as tf, numpy as np, pandas as pd
import os, json, pickle
def preprocess_transaction_dataframe(
    dataframe,
    user_col:str='user_id',
    item_col:str='item_id',
    time_col:str=None,
    min_items:int=20,
    save_file:str=None,
    drop_duplicates:bool=True
):
    '''
    Notes:
        - If `save_file` is not None, will save to both:
            - basename.ext, and
            - basename.overview.ext

    Arguments:
        dataframe (pd.DataFrame):
        user_col (str): the column name corresponding to the users. Defaults to
            `user_id`.
        item_col (str): the column name corresponding to the items. Defaults to
            `item_id`.
        time_col (str): the column name corresponding to when the interaction
            occured. By default None.
        min_items (int): minimum number of interactions the user should have to
            be included in the dataset. Defaults to 20.
        save_file (str): fullpath where to save the processed results. Defaults
            to None (no file is saved.)
        drop_duplicates (bool): Whether or not to remove repeat interactions.
            Defaults to True.

    Returns:
        dataframe (pd.DataFrame): filtered and processeded dataframe.
    '''
    dff = dataframe
    if drop_duplicates:
        dff = dff.drop_duplicates(subset=[user_col, item_col])

    # only users with at least `min_items` iteractions
    grouped = dff.groupby(user_col)
    dff = grouped.filter(lambda x: len(x) >= min_items)

    # for reindexing
    original_users = dff[user_col].unique()
    original_items = dff[item_col].unique()

    # database index to 0-based index
    user_map = {user: index for index, user in enumerate(original_users)}
    item_map = {item: index for index, item in enumerate(original_items)}

    # apply reindexing
    dff[user_col] = dff[user_col].apply(lambda user: user_map[user])
    dff[item_col] = dff[item_col].apply(lambda item: item_map[item])

    # dimensions of rating matrix
    num_users = len(original_users)
    num_items = len(original_items)

    # sort rating interactions by recency
    if time_col is not None:
        dff.sort_values(by=time_col, inplace=True)
        dff.sort_values([user_col, time_col], inplace=True, kind="mergesort")

        # The dataframe does not reconstruct indices in the sort or filter steps.
        dff = dff.reset_index()

    grouped = dff.groupby(user_col, group_keys=False)
    eval_df, train_df = grouped.tail(1), grouped.apply(lambda x: x.iloc[:-1])

    data = {
        'train_'+user_col: train_df[user_col].values.astype(np.int32),
        'train_'+item_col: train_df[item_col].values.astype(np.int32),

        'eval_'+user_col: eval_df[user_col].values.astype(np.int32),
        'eval_'+item_col: eval_df[item_col].values.astype(np.int32),

        'user_map': user_map,
        'item_map': item_map,

        'num_users': num_users,
        'num_items': num_items
    }
    if save_file:
        with open(save_file, 'wb') as f:
            pickle.dump(data, f)
        with open('{}.overview{}'.format(*os.path.splitext(save_file)), 'wb') as f:
            pickle.dump({
                k:v
                for k, v in data.items()
                if  k in ['user_map', 'item_map', 'num_users', 'num_items']
            }, f)
    return data
