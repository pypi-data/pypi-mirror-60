# Copyright (c) 2020 CRS4
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import numpy as np

from pyecvl._core.ecvl import (
    Image, DataType, ColorType, View_int8, View_int16, Neg, RearrangeChannels,
    CopyImage
)


def test_empty():
    img = Image()
    assert len(img.dims_) == 0
    assert img.IsEmpty()


def test_five_dims():
    dims = [1, 2, 3, 4, 5]
    img = Image(dims, DataType.uint8, "xyzoo", ColorType.none)
    assert img.dims_ == dims
    assert len(img.strides_) == len(dims)


def test_view():
    x = Image([5, 4, 3], DataType.int8, "xyc", ColorType.RGB)
    assert x.Channels() == 3
    assert x.IsOwner()
    y = View_int8(x)
    assert not y.IsOwner()
    y[1, 2, 0] = 36
    y[3, 3, 2] = 48
    y[4, 2, 1] = -127
    y[3, 2, 0] = -128
    Neg(x)
    assert y[1, 2, 0] == -36
    assert y[3, 3, 2] == -48
    assert y[4, 2, 1] == 127
    assert y[3, 2, 0] == -128


def test_rearrange_channels():
    S = [3, 4, 3, 2]
    img = Image(S, DataType.int16, "cxyz", ColorType.RGB)
    view = View_int16(img)
    for i in range(S[0]):
        for j in range(S[1]):
            for k in range(S[2]):
                for l in range(S[3]):
                    view[i, j, k, l] = (l + k * S[3] + j * S[2] * S[3] +
                                        i * S[1] * S[2] * S[3])
    img2 = Image()
    RearrangeChannels(img, img2, "xyzc")
    view2 = View_int16(img2)
    assert view2[2, 0, 1, 0] == view[0, 2, 0, 1]
    assert view2[3, 1, 1, 2] == view[2, 3, 1, 1]
    assert view2[0, 2, 0, 1] == view[1, 0, 2, 0]
    assert view2[1, 2, 0, 1] == view[1, 1, 2, 0]


def test_numpy():
    shape = [2, 3, 4]
    img = Image(shape, DataType.int16, "xy", ColorType.none)
    view = View_int16(img)
    a = np.array(img, copy=False)
    assert list(a.shape) == shape
    assert list(a.strides) == img.strides_
    assert a.dtype == np.int16
    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                assert a[i, j, k] == view[i, j, k]
    a.flat = 42
    b = np.array(img, copy=True)
    assert np.array_equal(a + img, a + b)


def test_numpy_types():
    shape, channels, color_type = [2, 3], "xy", ColorType.none
    for dt_name in ("int8", "int16", "int32", "int64",
                    "float32", "float64", "uint8", "uint16"):
        np_dt = getattr(np, dt_name)
        dt = getattr(DataType, dt_name)
        img = Image(shape, dt, channels, color_type)
        a = np.array(img, copy=False)
        assert a.dtype == np_dt


def test_image_from_array():
    channels, color_type = "xy", ColorType.none
    for dt_name in ("int8", "int16", "int32", "int64",
                    "float32", "float64", "uint8", "uint16"):
        np_dt = getattr(np, dt_name)
        dt = getattr(DataType, dt_name)
        a = np.arange(12).reshape(3, 4).astype(np_dt)
        b = np.asfortranarray(a)
        img = Image(b, channels, color_type)
        assert img.elemtype_ == dt
        assert img.dims_ == list(b.shape)
        assert img.strides_ == list(b.strides)
        # check construction from c-style array
        img = Image(a, channels, color_type)
        assert img.elemtype_ == dt
        assert img.dims_ == list(a.shape)
        assert img.strides_ == list(b.strides)
    a = np.arange(12).reshape(3, 4).astype(np.int16)
    b = np.asfortranarray(a)
    img = Image(b, channels, color_type)
    view = View_int16(img)
    for i in range(3):
        for j in range(4):
            assert view[i, j] == b[i, j]
    # check construction from c-style array
    img = Image(a, channels, color_type)
    view = View_int16(img)
    for i in range(3):
        for j in range(4):
            assert view[i, j] == a[i, j]


def test_add():
    x = Image([2, 4, 3], DataType.int8, "xyc", ColorType.RGB)
    y = Image([2, 4, 3], DataType.int8, "xyc", ColorType.RGB)
    a = np.array(x, copy=False)
    b = np.array(y, copy=False)
    a.fill(10)
    b.fill(3)
    x.Add(y)
    assert (a == 13).all()
    a.fill(10)
    x += y
    assert (a == 13).all()
    a.fill(10)
    b.fill(118)
    x.Add(y)
    assert (a == 127).all()
    a.fill(10)
    x.Add(y, saturate=False)
    assert (a == -128).all()


def test_sub():
    x = Image([2, 4, 3], DataType.int8, "xyc", ColorType.RGB)
    y = Image([2, 4, 3], DataType.int8, "xyc", ColorType.RGB)
    a = np.array(x, copy=False)
    b = np.array(y, copy=False)
    a.fill(-10)
    b.fill(3)
    x.Sub(y)
    assert (a == -13).all()
    a.fill(-10)
    x -= y
    assert (a == -13).all()
    a.fill(-10)
    b.fill(119)
    x.Sub(y)
    assert (a == -128).all()
    a.fill(-10)
    x.Sub(y, saturate=False)
    assert (a == 127).all()


def test_mul():
    x = Image([2, 4, 3], DataType.int8, "xyc", ColorType.RGB)
    y = Image([2, 4, 3], DataType.int8, "xyc", ColorType.RGB)
    a = np.array(x, copy=False)
    b = np.array(y, copy=False)
    a.fill(16)
    b.fill(3)
    x.Mul(y)
    assert (a == 48).all()
    a.fill(16)
    x *= y
    assert (a == 48).all()
    a.fill(16)
    b.fill(8)
    x.Mul(y)
    assert (a == 127).all()
    a.fill(16)
    x.Mul(y, saturate=False)
    assert (a == -128).all()


def test_div():
    x = Image([2, 4, 3], DataType.int8, "xyc", ColorType.RGB)
    y = Image([2, 4, 3], DataType.int8, "xyc", ColorType.RGB)
    a = np.array(x, copy=False)
    b = np.array(y, copy=False)
    a.fill(11)
    b.fill(2)
    x.Div(y)
    assert (a == 5).all()


def test_copy_image():
    dims, dtype, ch, ctype = [2, 4, 3], DataType.int8, "xyc", ColorType.RGB
    x = Image(dims, dtype, ch, ctype)
    a = np.array(x, copy=False)
    a.fill(3)
    # without dtype arg
    y = Image()
    CopyImage(x, y)
    assert y.dims_ == dims
    assert y.elemtype_ == dtype
    assert y.channels_ == ch
    assert y.colortype_ == ctype
    b = np.array(y, copy=False)
    assert (b == 3).all()
    # with dtype arg
    new_dtype = DataType.float32
    y = Image()
    CopyImage(x, y, new_dtype)
    assert y.dims_ == dims
    assert y.elemtype_ == new_dtype
    assert y.channels_ == ch
    assert y.colortype_ == ctype
    b = np.array(y, copy=False)
    assert (b == 3).all()
