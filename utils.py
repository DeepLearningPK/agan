import tensorflow as tf
import numpy as np
import cv2
import os
from PIL import Image

def to_array(path):
    try:
        img = tf.io.read_file('assets/' + path)
        img = tf.image.decode_image(img, channels=3)
        img = tf.image.convert_image_dtype(img, tf.float32)

        return (img - 0.5)*2
    except Exception as e:
        print(path, e)

def gen_batches(paths, batch_size):
    split_array = []
    section = tf.convert_to_tensor([to_array(paths[0])])
    i = 0

    for path in paths:
        img_tensor = to_array(path)
        if img_tensor is not None:
            if i == batch_size - 1:
                split_array.append(section)
                section = tf.convert_to_tensor([img_tensor])
                i = 0
            else:
                i += 1
                section = tf.concat([section, [img_tensor]], axis=0)

    return split_array

# Go from tensor output back to image
def to_image(tensor):
    # Scale from -1-1 to 0-255
    tensor = 255*(tensor + 1)/2
    # Make numpy array of bytes
    tensor = np.array(tensor, dtype=np.uint8)

    # If the image is wrapped in an extra dimension, remove it
    if np.ndim(tensor) > 3:
        # Make sure this isn't a list of multiple images
        assert tensor.shape[0] == 1
        # Get rid of the extra dimension
        tensor = tensor[0]

    # Initialize PIL Image using modified tensor
    return Image.fromarray(tensor)

def to_video(tensors, name):
    # Rescale from -1-1 to 0-255
    height, width, layers = tensors[0].shape
    size = (height, width)

    out = cv2.VideoWriter('./' + name + '.avi', cv2.VideoWriter_fourcc(*'DIVX'), 60, size)

    for i in range(len(tensors)):
        tensor = tensors[i]
        path = './frames/' + name + str(i) + '.png'
        to_image(tensor).save(path)

        frame = cv2.imread(path)
        out.write(frame)

        os.remove(path)

    out.release()
