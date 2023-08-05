import math

import numpy as np


def convert_conf(face_distances, face_match_threshold=0.6):
    """Calculates faces distance accuracy as a percentage.
    Args:
        face_distances (float): Face distance.
        face_match_threshold (float): Minimum distance error acceptable.
    Returns:
        float: Confidence score as a percentage.
    """
    if face_distances > face_match_threshold:
        rang = (1.0 - face_match_threshold)
        linear_val = (1.0 - face_distances) / (rang * 2.0)
        value = linear_val
    else:
        rang = face_match_threshold
        linear_val = 1.0 - (face_distances / (rang * 2.0))
        result = ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))
        value = linear_val + result
    return round(float(value), 2)


def face_distance(face_encoding_1, face_encoding_2):
    """Calculate norm from faces encodings.
    Args:
        face_encoding_1 (:obj:'list'): Faces encodings.
        face_encoding_2 (:obj:'list'): Faces encodings.
    Returns:
        float: Norm of the matrix.
    Raises:
        ValueError: Wrong base64 image.
    """
    encoding_1 = np.array([face_encoding_1])
    encoding_2 = np.array([face_encoding_2])
    if len(encoding_1) == 0:
        result = np.empty(0)
    else:
        result = np.linalg.norm(encoding_1 - encoding_2, axis=1)
    return convert_conf(result) * 100
