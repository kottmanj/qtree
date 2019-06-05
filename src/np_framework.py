"""
This file implements Numpy framework of the
simulator. It's main use is in conjunction with the :py:mod:`optimizer`
module, and example programs are listed in :py:mod:`cirq_test` module.
"""

import numpy as np
import copy
import src.operators as ops
import src.optimizer as opt
import src.utils as utils


def get_np_buckets(buckets, data_dict):
    """
    Takes buckets and returns their Numpy counterparts.

    Parameters
    ----------
    buckets : list of list
              buckets as returned by :py:meth:`circ2buckets`
              and :py:meth:`reorder_buckets`.
    data_dict : dict
              dictionary containing values for the placeholder Tensors
    Returns
    -------
    np_buckets : list of lists
               Buckets having Numpy tensors in place of gate labels
    """
    # import pdb
    # pdb.set_trace()

    # Create numpy buckets
    np_buckets = []
    for bucket in buckets:
        np_bucket = []
        for tensor in bucket:
            # sort tensor dimensions
            transpose_order = np.argsort(list(map(int, tensor.indices)))
            data = data_dict[tensor.data_key]

            new_tensor = tensor.copy(
                indices=(tensor.indices[pp] for pp in transpose_order),
                data=np.transpose(data.copy(), transpose_order))

            np_bucket.append(new_tensor)
        np_buckets.append(np_bucket)

    return np_buckets


def slice_np_buckets(np_buckets, slice_dict):
    """
    Takes slices of the tensors in Numpy buckets
    over the variables in idx_parallel.

    Parameters
    ----------
    np_buckets : list of lists
              Buckets containing Numpy tensors
    slice_dict : dict
              Current subtensor along the sliced variables
              in the form {variable: slice}
    Returns
    -------
    sliced_buckets : list of lists
              buckets with sliced tensors
    """
    # import pdb
    # pdb.set_trace()

    # Create tf buckets from unordered buckets
    sliced_buckets = []
    for bucket in np_buckets:
        sliced_bucket = []
        for tensor in bucket:
            slice_bounds = []
            for idx in tensor.indices:
                try:
                    slice_bounds.append(slice_dict[idx])
                except KeyError:
                    slice_bounds.append(slice(None))
            sliced_bucket.append(
                tensor.copy(data=tensor.data[tuple(slice_bounds)])
            )
        sliced_buckets.append(sliced_bucket)

    return sliced_buckets


def process_bucket_np(bucket):
    """
    Process bucket in the bucket elimination algorithm.
    We multiply all tensors in the bucket and sum over the
    variable which the bucket corresponds to. This way the
    variable of the bucket is removed from the expression.

    Parameters
    ----------
    bucket : list
           List containing tuples of tensors (gates) with their indices.

    Returns
    -------
    tensor : optimizer.Tensor
           wrapper tensor object holding the result
    """
    result_indices = bucket[0].indices
    result_data = bucket[0].data

    for tensor in bucket[1:]:
        expr = utils.get_einsum_expr(
            list(map(int, result_indices)), list(map(int, tensor.indices))
        )

        result_data = np.einsum(expr, result_data, tensor.data)

        # Merge and sort indices and shapes
        result_indices = tuple(sorted(
            set(result_indices + tensor.indices),
            key=int)
        )

    if len(result_indices) > 0:
        first_index, *result_indices = result_indices
        tag = first_index.identity
    else:
        tag = 'f'
        result_indices = []

    # reduce
    result = opt.Tensor(f'E{tag}', result_indices,
                        data=np.sum(result_data, axis=0))
    return result
