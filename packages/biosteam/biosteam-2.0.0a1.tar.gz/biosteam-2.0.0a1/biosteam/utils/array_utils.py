# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 16:42:49 2018

This module includes classes and functions relating arrays.

@author: Guest Group
"""
import numpy as np
from array_collections import PropertyFactory, tuple_array, property_array

__all__ = ('tuple_array', 'property_array',
           'PropertyFactory', 'fraction')

ndarray = np.ndarray
asarray = np.asarray

# %% Functions

# def reorder(array: 'array_like', current_order: tuple, new_order: tuple) -> np.ndarray:
#     """Return a reordered array with zero in place of elements that exist in the new order but not in the current order.
    
#     .. code-block:: python
       
#        >>> reorder([1,2,3], ('a', 'b', 'c'), ('a', 'c', 'd', 'b'))
#        array([1, 3, 0, 2])
    
#     """
#     n = 0
#     p_new = np.zeros(len(new_order), dtype=float)
#     for ID1 in current_order:
#         m = 0
#         for ID2 in new_order:
#             if ID1 is ID2:
#                 p_new[m] = array[n]
#             m += 1
#         n += 1
#     return p_new

def fraction(array):
    """Return a normalized array to a magnitude of 1. If magnitude is zero, all fractions will have equal value."""
    sum_array = array.sum()
    if sum_array == 0:
        l = len(array)
        return np.ones(l)/l
    else:
        return array/sum_array
    
# def same_type(iterable, type_):
#     """Raise TypeError if any item in iterable is not an instance of type_."""
#     # Make sure iterable is in a tuple
#     if not isinstance(iterable, type_):
#         # Check that all are type_ instances
#         for s in iterable:
#             if not isinstance(s, type_):
#                 raise TypeError(f"Only '{type_.__name__}' objects are valid elements, not '{type(s).__name__}' objects.")