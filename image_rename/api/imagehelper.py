import numpy as np
from typing import Union, List
import cv2


def append_image_to_news(src_img: np.array,
                         list_append_img: Union[np.ndarray, List[np.ndarray]], direction: str):
    """
    It's easier to let you concatenate images together.

    USAGE:
        - append_image_to_news(org_img, [crop_img], direction='bottom')
        - append_image_to_news(org_img, [crop_img, img2], direction='r')
        - cv2.imshow('i', append_image_to_news(...)), cv2.waitKey(0)

    .. note::

        the hstack and vstack are similar to this function, but the arrays must have the same shape
        np.hstack((arr1, arr2))  # direction 'r'
        np.vstack((arr1, arr2))  # direction 's'

    """
    direction = direction.lower()
    if isinstance(list_append_img, np.ndarray):
        list_append_img = [list_append_img]

    new_image = src_img.copy()
    for append_img in list_append_img:
        target_list = [new_image, append_img]
        for idx, img in enumerate(target_list):
            if img.dtype != np.uint8:  # Unsupported depth of input image. where 'depth' is 4 (CV_32S)
                img = img.astype(np.uint8)  # or float32
            if len(img.shape) < 3:
                target_list[idx] = cv2.cvtColor(img, cv2.COLOR_GRAY2RGBA)
            elif img.shape[2] < 4:
                target_list[idx] = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
        new_image, append_img = target_list

        src_h, src_w, *src_channel = new_image.shape
        src_channel = src_channel[0] if src_channel else 1
        a_h, a_w, *target_channel = append_img.shape
        target_channel = target_channel[0] if target_channel else 1

        channel = max(src_channel, target_channel)

        if direction in ('e', 'r', 'w', 'l'):
            concat_img = np.zeros((max(src_h, a_h), src_w + a_w, channel), dtype=np.uint8)
        else:
            concat_img = np.zeros((src_h + a_h, max(src_w, a_w), channel), dtype=np.uint8)

        if direction in ('e', 'r'):  # append to right
            concat_img[:src_h, :src_w, :] = new_image
            concat_img[:a_h, src_w: src_w + a_w, :] = append_img
        elif direction in ('w', 'l'):  # append to left
            concat_img[:a_h, : a_w, :] = append_img
            concat_img[:src_h, a_w: a_w + src_w, :] = new_image
        elif direction in ('n', 't'):  # append to top
            concat_img[:a_h, : a_w, :] = append_img
            concat_img[a_h:a_h + src_h, : src_w, :] = new_image
        else:  # append to bottom
            concat_img[:src_h, : src_w, :] = new_image
            concat_img[src_h:src_h + a_h, : a_w, :] = append_img
        new_image = concat_img
    return new_image
