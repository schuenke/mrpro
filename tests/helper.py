"""Helper/Utilities for test functions."""

# Copyright 2023 Physikalisch-Technische Bundesanstalt
#
# Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import torch


def relative_image_difference(img1, img2):
    """Calculate mean absolute relative difference between two images.

    Parameters
    ----------
    img1
        first image
    img2
        second image

    Returns
    -------
        mean absolute relative difference between images
    """
    image_difference = torch.mean(torch.abs(img1 - img2))
    image_mean = 0.5 * torch.mean(torch.abs(img1) + torch.abs(img2))
    if image_mean == 0:
        raise ValueError('average of images should be larger than 0')
    return image_difference / image_mean


def dotproduct_adjointness_test(
    operator, u: torch.Tensor, v: torch.Tensor, relative_tolerance: float = 1e-3, absolute_tolerance=1e-5
):
    """Test the adjointness of operator and operator.H

    Test if
         <Operator(u),v> == <u, Operator^H(v)>
         for one u ∈ domain and one v ∈ range of Operator.
    and if the shapes match.

    Note: This property should hold for all u and v.
    Commonly, this function is called with two random vectors u and v.


    Parameters
    ----------
    operator
        operator
    u
        element of the domain of the operator
    v
        element of the range of the operator
    relative_tolerance
        default is pytorch's default for float16
    absolute_tolerance
        default is pytorch's default for float16

    Raises
    ------
    AssertionError
        if the adjointness property does not hold
    AssertionError
        if the shape of operator(u) and v does not match
        if the shape of u and operator.H(v) does not match

    """
    (forward_u,) = operator(u)
    (adjoint_v,) = operator.adjoint(v)

    # explicitly check the shapes, as flatten makes the dot product insensitive to wrong shapes
    assert forward_u.shape == v.shape
    assert adjoint_v.shape == u.shape

    dotproduct_range = torch.vdot(forward_u.flatten(), v.flatten())
    dotproduct_domain = torch.vdot(u.flatten().flatten(), adjoint_v.flatten())
    torch.testing.assert_close(dotproduct_range, dotproduct_domain, rtol=relative_tolerance, atol=absolute_tolerance)
