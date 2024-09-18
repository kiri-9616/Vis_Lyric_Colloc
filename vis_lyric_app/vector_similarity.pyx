import cython
from libc.math cimport sqrt
import numpy as np
cimport numpy as np


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef double cosine_similarity(np.ndarray[np.float32_t, ndim=1, mode="c"] vec1, np.ndarray[np.float32_t, ndim=1, mode="c"] vec2):
    cdef int n = vec1.shape[0]
    cdef double dot_product = 0.0
    cdef double norm_vec1 = 0.0
    cdef double norm_vec2 = 0.0
    cdef int i

    for i in range(n):
        dot_product += vec1[i] * vec2[i]
        norm_vec1 += vec1[i] * vec1[i]
        norm_vec2 += vec2[i] * vec2[i]

    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0.0  # avoid division by zero

    return dot_product / (sqrt(norm_vec1) * sqrt(norm_vec2))

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef double batch_max_cosine_similarity(np.ndarray[np.float32_t, ndim=1, mode="c"] query_vec, np.ndarray[np.float32_t, ndim=2, mode="c"] phrase_vecs):
    cdef double max_similarity = 0.0
    cdef int i
    cdef double similarity

    for i in range(phrase_vecs.shape[0]):
        similarity = cosine_similarity(query_vec, phrase_vecs[i])
        if similarity > max_similarity:
            max_similarity = similarity

    return max_similarity
