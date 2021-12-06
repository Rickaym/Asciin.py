from typing import Any
from tests.utils import move_somewhere, change_each, change_summation, transform_somewhere
from Asciinpy._2D import Mask


def test_dimension():
    obj = Mask([1, 1], "#ie\n@#\n#")

    assert obj.dimension.tolist() == [3, 3]


def test_midpoint():
    obj = Mask([0, 0], "#####\n#####\n#####")
    sval = [2, 1]
    for i in range(20):
        assert obj.midpoint.tolist() == sval
        moved = move_somewhere(obj)
        sval = [sval[0] + moved[0], sval[1] + moved[1]]


def test_transform():
    for i in range(200):
        obj = Mask([0, 0], "####\n####\n####")
        prior: Any = obj.occupancy
        lmove = change_each(prior.tolist(), transform_somewhere(obj))
        assert lmove == obj.occupancy.tolist()


def test_movement():
    obj = Mask([0, 0], "####\n####\n####")
    for i in range(20):
        prior = obj.occupancy.sum(axis=0)
        moved = change_summation(obj.occupancy, move_somewhere(obj))
        assert (prior + moved).tolist() == obj.occupancy.sum(axis=0).tolist()

        lmove = change_each(obj.occupancy.tolist(), lambda at, dist: [at[0]+dist[0], at[1]+dist[1]], move_somewhere(obj))
        assert lmove == obj.occupancy.tolist()
