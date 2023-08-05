import tensorflow as tf, numpy as np

def shared_shuffle(arrays):
    '''
    Utility function that shuffles a series of arrays with the same length together
    '''
    idx = np.arange(len(arrays[0]))
    np.random.shuffle(idx)
    return (arr[idx] for arr in arrays)

def shared_sort(arrays, which=0):
    '''
    Utility function that sorts a series of arrays with the same length together
    Arguments:
        arrays (list): a list of arrays with each of the same length
        which (int): The array to use for sorting. Defaults to `0`.
    '''
    idx = np.argsort(arrays[which])
    return (arr[idx] for arr in arrays)

def numeric_breaks(arr:list):
    '''
    Arguments:
        arr (list): a list of sorted numbers where any number may occur multiple
            times, e.g. `[1,1,1,1,1,2,2,2,3,3,3,3,3,4,4]`.
    Returns:
        bounds (list): a list of the indicies corresponding to the start / stop
            of each unique number. e.g. `[0, 5, 9, 14, 15]`
    '''
    inner_bounds = np.argwhere(arr[1:] - arr[:-1])[:, 0] + 1
    (upper_bound,) = arr.shape
    index_bounds = [0] + inner_bounds.tolist() + [upper_bound]
    return index_bounds

def batch_idx(i, batch_size):
    '''
    Utility function specific to get the bounds of a batch.
    '''
    return i * batch_size, (i + 1) * batch_size

def mask_duplicates(x, axis=1):  # type: (np.ndarray, int) -> np.ndarray
    """Identify duplicates from sampling with replacement.
    Args:
    x: A 2D NumPy array of samples
    axis: The axis along which to de-dupe.
    Returns:
    A NumPy array with the same shape as x with one if an element appeared
    previously along axis 1, else zero.
    """
    if axis != 1:
        raise NotImplementedError

    x_sort_ind = np.argsort(x, axis=1, kind="mergesort")
    sorted_x = x[np.arange(x.shape[0])[:, np.newaxis], x_sort_ind]

    # compute the indices needed to map values back to their original position.
    inv_x_sort_ind = np.argsort(x_sort_ind, axis=1, kind="mergesort")

    # Compute the difference of adjacent sorted elements.
    diffs = sorted_x[:, :-1] - sorted_x[:, 1:]

    # We are only interested in whether an element is zero. Therefore left padding
    # with ones to restore the original shape is sufficient.
    diffs = np.concatenate([
        np.ones((diffs.shape[0], 1), dtype=diffs.dtype),
        diffs
    ], axis=1)

    # Duplicate values will have a difference of zero. By definition the first
    # element is never a duplicate.
    return np.where(diffs[np.arange(x.shape[0])[:, np.newaxis], inv_x_sort_ind], 0, 1)
