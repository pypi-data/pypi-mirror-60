# BSD 3-Clause License; see https://github.com/jpivarski/awkward-1.0/blob/master/LICENSE

import sys
import itertools

import pytest
import numpy

import awkward1

content = awkward1.layout.NumpyArray(numpy.array([0.0, 1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9]));
offsets = awkward1.layout.Index64(numpy.array([0, 3, 3, 5, 6, 10, 10]))
listoffsetarray = awkward1.layout.ListOffsetArray64(offsets, content)
regulararray = awkward1.layout.RegularArray(listoffsetarray, 2)
starts = awkward1.layout.Index64(numpy.array([0, 1]))
stops = awkward1.layout.Index64(numpy.array([2, 3]))
listarray = awkward1.layout.ListArray64(starts, stops, regulararray)

def test_type():
    assert str(awkward1.typeof(regulararray)) == "2 * var * float64"

def test_iteration():
    assert awkward1.tolist(regulararray) == [[[0.0, 1.1, 2.2], []], [[3.3, 4.4], [5.5]], [[6.6, 7.7, 8.8, 9.9], []]]

def test_tojson():
    assert awkward1.tojson(regulararray) == "[[[0.0,1.1,2.2],[]],[[3.3,4.4],[5.5]],[[6.6,7.7,8.8,9.9],[]]]"

def test_getitem_at():
    assert awkward1.tolist(regulararray[0]) == [[0.0, 1.1, 2.2], []]
    assert awkward1.tolist(regulararray[1]) == [[3.3, 4.4], [5.5]]
    assert awkward1.tolist(regulararray[2]) == [[6.6, 7.7, 8.8, 9.9], []]

def test_getitem_range():
    assert awkward1.tolist(regulararray[1:]) == [[[3.3, 4.4], [5.5]], [[6.6, 7.7, 8.8, 9.9], []]]
    assert awkward1.tolist(regulararray[:-1]) == [[[0.0, 1.1, 2.2], []], [[3.3, 4.4], [5.5]]]

def test_getitem():
    assert awkward1.tolist(regulararray[(0,)]) == [[0.0, 1.1, 2.2], []]
    assert awkward1.tolist(regulararray[(1,)]) == [[3.3, 4.4], [5.5]]
    assert awkward1.tolist(regulararray[(2,)]) == [[6.6, 7.7, 8.8, 9.9], []]
    assert awkward1.tolist(regulararray[(slice(1, None, None),)]) == [[[3.3, 4.4], [5.5]], [[6.6, 7.7, 8.8, 9.9], []]]
    assert awkward1.tolist(regulararray[(slice(None, -1, None),)]) == [[[0.0, 1.1, 2.2], []], [[3.3, 4.4], [5.5]]]

def test_getitem_deeper():
    assert awkward1.tolist(listarray) == [[[[0.0, 1.1, 2.2], []], [[3.3, 4.4], [5.5]]], [[[3.3, 4.4], [5.5]], [[6.6, 7.7, 8.8, 9.9], []]]]

    assert awkward1.tolist(listarray[0, 0, 0]) == [0.0, 1.1, 2.2]
    assert awkward1.tolist(listarray[0, 0, 1]) == []
    assert awkward1.tolist(listarray[0, 1, 0]) == [3.3, 4.4]
    assert awkward1.tolist(listarray[0, 1, 1]) == [5.5]
    assert awkward1.tolist(listarray[1, 0, 0]) == [3.3, 4.4]
    assert awkward1.tolist(listarray[1, 0, 1]) == [5.5]
    assert awkward1.tolist(listarray[1, 1, 0]) == [6.6, 7.7, 8.8, 9.9]
    assert awkward1.tolist(listarray[1, 1, 1]) == []

    assert awkward1.tolist(listarray[0, 0, 0:]) == [[0.0, 1.1, 2.2], []]
    assert awkward1.tolist(listarray[0, 0, 1:]) == [[]]
    assert awkward1.tolist(listarray[0, 1, 0:]) == [[3.3, 4.4], [5.5]]
    assert awkward1.tolist(listarray[0, 1, 1:]) == [[5.5]]
    assert awkward1.tolist(listarray[1, 0, 0:]) == [[3.3, 4.4], [5.5]]
    assert awkward1.tolist(listarray[1, 0, 1:]) == [[5.5]]
    assert awkward1.tolist(listarray[1, 1, 0:]) == [[6.6, 7.7, 8.8, 9.9], []]
    assert awkward1.tolist(listarray[1, 1, 1:]) == [[]]

    assert awkward1.tolist(listarray[[1], 0, 0:]) == [[[3.3, 4.4], [5.5]]]
    assert awkward1.tolist(listarray[[1, 0], 0, 0:]) == [[[3.3, 4.4], [5.5]], [[0.0, 1.1, 2.2], []]]

    assert awkward1.tolist(listarray[:, :, [0, 1]]) == [[[[0.0, 1.1, 2.2], []], [[3.3, 4.4], [5.5]]], [[[3.3, 4.4], [5.5]], [[6.6, 7.7, 8.8, 9.9], []]]]
    assert awkward1.tolist(listarray[:, :, [1, 0]]) == [[[[], [0.0, 1.1, 2.2]], [[5.5], [3.3, 4.4]]], [[[5.5], [3.3, 4.4]], [[], [6.6, 7.7, 8.8, 9.9]]]]
    assert awkward1.tolist(listarray[:, :, [1, 0, 1]]) == [[[[], [0.0, 1.1, 2.2], []], [[5.5], [3.3, 4.4], [5.5]]], [[[5.5], [3.3, 4.4], [5.5]], [[], [6.6, 7.7, 8.8, 9.9], []]]]
    assert awkward1.tolist(listarray[:, :2, [0, 1]]) == [[[[0.0, 1.1, 2.2], []], [[3.3, 4.4], [5.5]]], [[[3.3, 4.4], [5.5]], [[6.6, 7.7, 8.8, 9.9], []]]]

    assert awkward1.tolist(listarray[:1, [0, 0, 1, 1], [0, 1, 0, 1]]) == [[[0.0, 1.1, 2.2], [], [3.3, 4.4], [5.5]]]
    assert awkward1.tolist(listarray[:1, [1, 1, 0, 0], [1, 0, 1, 0]]) == [[[5.5], [3.3, 4.4], [], [0.0, 1.1, 2.2]]]

content2 = awkward1.layout.NumpyArray(numpy.arange(2*3*5*7).reshape(-1, 7))
regulararrayA = awkward1.layout.RegularArray(content2, 5)
regulararrayB = awkward1.layout.RegularArray(regulararrayA, 3)
modelA = numpy.arange(2*3*5*7).reshape(2*3, 5, 7)
modelB = numpy.arange(2*3*5*7).reshape(2, 3, 5, 7)

def test_numpy():
    assert awkward1.tolist(regulararrayA) == awkward1.tolist(modelA)
    assert awkward1.tolist(regulararrayB) == awkward1.tolist(modelB)

    for depth in 0, 1, 2, 3:
        for cuts in itertools.permutations((0, 1, 4, -5), depth):
            assert awkward1.tolist(modelA[cuts]) == awkward1.tolist(regulararrayA[cuts])

    for depth in 0, 1, 2, 3:
        for cuts in itertools.permutations((slice(None), slice(1, None), slice(None, -1), slice(None, None, 2)), depth):
            assert awkward1.tolist(modelA[cuts]) == awkward1.tolist(regulararrayA[cuts])

    for depth in 0, 1, 2, 3:
        for cuts in itertools.permutations((slice(1, None), slice(None, -1), 2, -2), depth):
            assert awkward1.tolist(modelA[cuts]) == awkward1.tolist(regulararrayA[cuts])

    for depth in 0, 1, 2, 3:
        for cuts in itertools.permutations(([2, 0, 0, 1], [1, -2, 0, -1], 2, -2), depth):
            assert awkward1.tolist(modelA[cuts]) == awkward1.tolist(regulararrayA[cuts])

    for depth in 0, 1, 2, 3:
        for cuts in itertools.permutations(([2, 0, 0, 1], [1, -2, 0, -1], slice(1, None), slice(None, -1)), depth):
            cuts = cuts
            while len(cuts) > 0 and isinstance(cuts[0], slice):
                cuts = cuts[1:]
            while len(cuts) > 0 and isinstance(cuts[-1], slice):
                cuts = cuts[:-1]
            if any(isinstance(x, slice) for x in cuts):
                continue
            assert awkward1.tolist(modelA[cuts]) == awkward1.tolist(regulararrayA[cuts])

    for depth in 0, 1, 2, 3, 4:
        for cuts in itertools.permutations((-2, -1, 0, 1, 1), depth):
            assert awkward1.tolist(modelB[cuts]) == awkward1.tolist(regulararrayB[cuts])

    for depth in 0, 1, 2, 3, 4:
        for cuts in itertools.permutations((-1, 0, 1, slice(1, None), slice(None, -1)), depth):
            assert awkward1.tolist(modelB[cuts]) == awkward1.tolist(regulararrayB[cuts])

    for depth in 0, 1, 2, 3, 4:
        for cuts in itertools.permutations((-1, 0, [1, 0, 0, 1], [0, 1, -1, 1], slice(None, -1)), depth):
            cuts = cuts
            while len(cuts) > 0 and isinstance(cuts[0], slice):
                cuts = cuts[1:]
            while len(cuts) > 0 and isinstance(cuts[-1], slice):
                cuts = cuts[:-1]
            if any(isinstance(x, slice) for x in cuts):
                continue
            assert awkward1.tolist(modelB[cuts]) == awkward1.tolist(regulararrayB[cuts])

def test_setidentities():
    regulararray.setidentities()
    assert numpy.asarray(regulararray.identities).tolist() == [
        [0],
        [1],
        [2]]
    assert numpy.asarray(regulararray.content.identities).tolist() == [
        [0, 0],
        [0, 1],
        [1, 0],
        [1, 1],
        [2, 0],
        [2, 1]]
    assert numpy.asarray(regulararray.content.content.identities).tolist() == [
        [0, 0, 0],   # 0.0
        [0, 0, 1],   # 1.1
        [0, 0, 2],   # 2.2
      # [0, 1,  ],   # (empty list)
        [1, 0, 0],   # 3.3
        [1, 0, 1],   # 4.4
        [1, 1, 0],   # 5.5
        [2, 0, 0],   # 6.6
        [2, 0, 1],   # 7.7
        [2, 0, 2],   # 8.8
        [2, 0, 3]]   # 9.9
      # [2, 1,  ],   # (empty list)

    regulararrayB.setidentities()
    assert numpy.asarray(regulararrayB.identities).tolist() == [
        [0],
        [1]]
    assert numpy.asarray(regulararrayB.content.identities).tolist() == [
        [0, 0],
        [0, 1],
        [0, 2],
        [1, 0],
        [1, 1],
        [1, 2]]

numba = pytest.importorskip("numba")

def test_numba():
    content = awkward1.layout.NumpyArray(numpy.array([0.0, 1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9]));
    offsets = awkward1.layout.Index64(numpy.array([0, 3, 3, 5, 6, 10, 10]))
    listoffsetarray = awkward1.layout.ListOffsetArray64(offsets, content)
    regulararray = awkward1.layout.RegularArray(listoffsetarray, 2)
    regulararray_m1 = awkward1.layout.RegularArray(listoffsetarray[:-1], 2)
    regulararray_m2 = awkward1.layout.RegularArray(listoffsetarray[:-2], 2)
    starts = awkward1.layout.Index64(numpy.array([0, 1]))
    stops = awkward1.layout.Index64(numpy.array([2, 3]))
    listarray = awkward1.layout.ListArray64(starts, stops, regulararray)

    @numba.njit
    def f1(q):
        return 3.14

    assert sys.getrefcount(regulararray) == 2
    f1(regulararray)
    assert sys.getrefcount(regulararray) == 2

    @numba.njit
    def f2(q):
        return q

    assert sys.getrefcount(regulararray) == 2
    assert awkward1.tolist(f2(regulararray)) == awkward1.tolist(regulararray)
    assert sys.getrefcount(regulararray) == 2

    @numba.njit
    def f3(q):
        return len(q)

    assert f3(regulararray) == 3
    assert f3(regulararray_m1) == 2
    assert f3(regulararray_m2) == 2
    assert len(regulararray) == 3
    assert len(regulararray_m1) == 2
    assert len(regulararray_m2) == 2

    @numba.njit
    def f4(q):
        return q[1]

    assert awkward1.tolist(f4(regulararray)) == [[3.3, 4.4], [5.5]]

    @numba.njit
    def f5(q, i):
        return q[i]

    assert awkward1.tolist(f5(regulararray, 1)) == [[3.3, 4.4], [5.5]]

    @numba.njit
    def f6(q, i):
        return q[i]

    assert awkward1.tolist(f6(regulararray, slice(1, None))) == awkward1.tolist(regulararray[slice(1, None)]) == [[[3.3, 4.4], [5.5]], [[6.6, 7.7, 8.8, 9.9], []]]
    assert awkward1.tolist(f6(regulararray, slice(None, -1))) == awkward1.tolist(regulararray[slice(None, -1)]) == [[[0.0, 1.1, 2.2], []], [[3.3, 4.4], [5.5]]]

    @numba.njit
    def f7(q, i):
        return q[(i,)]

    assert awkward1.tolist(f7(regulararray, 1)) == [[3.3, 4.4], [5.5]]

    @numba.njit
    def f8(q, i):
        return q[:, i]

    assert awkward1.tolist(f8(listarray, 1)) == awkward1.tolist(listarray[:, 1]) == [[[3.3, 4.4], [5.5]], [[6.6, 7.7, 8.8, 9.9], []]]

    @numba.njit
    def f9(q):
        return q[:, 1, 0]

    assert awkward1.tolist(listarray[:, 1, 0]) == awkward1.tolist(f9(listarray)) == [[3.3, 4.4], [6.6, 7.7, 8.8, 9.9]]

    @numba.njit
    def f10(q, i):
        return q[:, 1, i]

    assert awkward1.tolist(f10(listarray, slice(None, 1))) == awkward1.tolist(listarray[:, 1, slice(None, 1)]) == [[[3.3, 4.4]], [[6.6, 7.7, 8.8, 9.9]]]
    assert awkward1.tolist(f10(listarray, slice(None, None))) == [[[3.3, 4.4], [5.5]], [[6.6, 7.7, 8.8, 9.9], []]]
    assert awkward1.tolist(f10(listarray, slice(None, None, -1))) == [[[5.5], [3.3, 4.4]], [[], [6.6, 7.7, 8.8, 9.9]]]

    @numba.njit
    def f11(q, i):
        return q[[0, 1], 1, i]

    assert awkward1.tolist(f11(listarray, slice(None, 1))) == awkward1.tolist(listarray[[0, 1], 1, slice(None, 1)]) == [[[3.3, 4.4]], [[6.6, 7.7, 8.8, 9.9]]]

    @numba.njit
    def f12(q):
        return q[:, 1:, [1, 0, 1]]

    assert awkward1.tolist(f12(listarray)) == awkward1.tolist(listarray[:, 1:, [1, 0, 1]]) == [[[[5.5], [3.3, 4.4], [5.5]]], [[[], [6.6, 7.7, 8.8, 9.9], []]]]

    @numba.njit
    def f13(q):
        return q[:, [1], [1, 0, 1]]

    assert awkward1.tolist(f13(listarray)) == awkward1.tolist(listarray[:, [1], [1, 0, 1]]) == [[[5.5], [3.3, 4.4], [5.5]], [[], [6.6, 7.7, 8.8, 9.9], []]]

    @numba.njit
    def f14(q):
        return q.content

    assert awkward1.tolist(f14(regulararray)) == awkward1.tolist(regulararray.content)

    @numba.njit
    def f15(q):
        return q.size

    assert awkward1.tolist(f15(regulararray)) == awkward1.tolist(regulararray.size) == 2
