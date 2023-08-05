# BSD 3-Clause License
#
# Copyright (c) 2019, Doug Davis
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__doc__ = "Calculate histograms with blazing speed."

__version__ = "0.0.1"
version_info = tuple(__version__.split("."))

import numpy as np
from histmp._CPP import _f1dw, _v1dw, _omp_get_max_threads


def omp_get_max_threads():
    """Get the number of threads available to OpenMP.

    This returns the result of calling the OpenMP C function
    `of the same name
    <https://www.openmp.org/spec-html/5.0/openmpsu112.html>`_.

    Returns
    -------
    int
        the maximum number of available threads

    """
    return _omp_get_max_threads()


def histogram(x, bins=10, range=None, weights=None, flow=False):
    """Calculate a histogram for one dimensional data.

    Parameters
    ----------
    x : array_like
        the data to histogram
    bins : int or array_like
        if ``int``: the number of bins; if ``array_like``: the bin edges
    range : tuple(float, float), optional
        the definition of the edges of the bin range (start, stop)
    weights : array_like, optional
        a set of weights associated with the elements of ``x``
    flow : bool
        if ``True``, include under/overflow in the first/last bins

    Returns
    -------
    :py:obj:`numpy.ndarray`
        the bin counts
    :py:obj:`numpy.ndarray`
        the standard error of each bin count, :math:`\sqrt{\sum_i w_i^2}`

    """
    x = np.ascontiguousarray(x)
    if weights is not None:
        weights = np.ascontiguousarray(weights)
    else:
        weights = np.ones_like(x, order="C")

    if isinstance(bins, int):
        if range is not None:
            start, stop = range[0], range[1]
        else:
            start, stop = np.amin(x), np.amax(x)
        return _f1dw(x, weights, bins, start, stop, flow, True)

    else:
        if range is not None:
            raise TypeError("range must be None if bins is non-int")
        bins = np.ascontiguousarray(bins)
        return _v1dw(x, weights, bins, flow, True)
