"""[summary]
"""
import tensorflow as tf


def info():
    """[summary]
    """
    print("Num GPUs Available: ",
          len(tf.config.experimental.list_physical_devices('GPU')))


def only_use_gpu(device):
    """[summary]
    Args:
        device ([type]): [description]
    """
    tf.config.experimental.set_visible_devices(device, 'GPU')
