import tensorflow as tf
def get_gpus():
    '''
    shorthand wrapper for `tf.config.experimental.list_physical_devices`
    Arguments:
        None
    Retuns:
        gpus (list): list of tf.Devices corresponding to physical gpus on device.
    '''
    return tf.config.experimental.list_physical_devices('GPU')

def set_gpus(
    gpus:list,
    allow_growth:bool=True,
    limit_memory:bool=False,
    gbs:float=None
) -> None:
    '''
    Arguments:
        gpus (list): list of tf.Devices to limit session to.

        allow_growth (bool): Whether or not to allow GPU memory growth for every
            gpu in `gpus`. Defaults to `True`.

        limit_memory (bool): Whether or not to limit the memory of each gpu in
            `gpus` to `gbs` number of gigabytes. Defaults to `False`.

        gbs (float): how many gigabytes to limit gpu memory to. Only used if
            `limit_memory=True`

    Returns:
        None
    '''
    gb = 1024
    if not gpus:
        return
    # Restrict TensorFlow to only allocate 1GB of memory on the first GPU
    try:
        tf.config.experimental.set_visible_devices(gpus, 'GPU')

        if allow_growth:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)


        if limit_memory and gbs is not None:
            for gpu in gpus:
                tf.config.experimental.set_virtual_device_configuration(
                    gpu,
                    [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=gbs*gb)]
                )

        logical_gpus = tf.config.experimental.list_logical_devices('GPU')
        print(len(get_gpus()), "Physical GPUs", len(logical_gpus), "Logical GPUs")
    except RuntimeError as e:
        # Virtual devices must be set before GPUs have been initialized
        print(e)
