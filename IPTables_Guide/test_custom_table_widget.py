from typing import Dict
from custom_table_widget import CustomTableWidget, Row

from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton
import pytest


def test_initializing(qtbot):
    c1: CustomTableWidget = CustomTableWidget()
    assert c1.row_types == []
    assert c1.rows == []
    assert isinstance(c1.main_layout, QGridLayout)
    assert c1.layout() == c1.main_layout
    assert c1.main_layout.horizontalSpacing() == 0
    assert c1.main_layout.verticalSpacing() == 0
    c1.deleteLater()

    c2: CustomTableWidget = CustomTableWidget([], None)
    assert c2.row_types == []
    assert c2.rows == []
    assert isinstance(c2.main_layout, QGridLayout)
    assert c2.layout() == c2.main_layout
    assert c2.main_layout.horizontalSpacing() == 0
    assert c2.main_layout.verticalSpacing() == 0
    c2.deleteLater()

    c3: CustomTableWidget = CustomTableWidget(
        [("everything is fabulous", QWidget)])
    assert c3.row_types == [("everything is fabulous", QWidget)]
    assert c3.rows == []
    assert c3.layout() == c3.main_layout
    assert isinstance(c3.main_layout, QGridLayout)
    assert c3.main_layout.horizontalSpacing() == 0
    assert c3.main_layout.verticalSpacing() == 0
    c3.deleteLater()


def test_getitem(qtbot):
    c1: CustomTableWidget = CustomTableWidget(
        [("alpha", QWidget), ("beta", QPushButton), ("gamma", QLabel)]
    )
    c1.add_row()
    c1.add_row()
    c1.add_row()
    keys = ["alpha", "beta", "gamma"]
    types = {}
    for k, t in c1.row_types:
        types[k] = t
    assert keys == [k for k, _ in c1.row_types]
    for i in range(3):
        assert isinstance(c1[i], Dict)
        assert len(c1[i]) == 3  # type: ignore
        l = list(c1[i].keys())  # type: ignore
        l.sort()
        assert l == keys
        assert c1[i].keys() == c1[0].keys()  # type: ignore
        for k in keys:
            assert isinstance(c1[(i, k)], QWidget)
            assert c1[i][k] == c1[(i, k)]  # type: ignore
            assert isinstance(c1[(i, k)], types[k])
            assert c1[((i, k))] == \
                c1.main_layout.itemAtPosition(i, keys.index(k)).widget()

    assert len(c1[:2]) == 2  # type: ignore
    assert len(c1[:3]) == 3  # type: ignore
    assert len(c1[2:3]) == 1  # type: ignore
    assert len(c1[1:2]) == 1  # type: ignore
    assert len(c1[0:2]) == 2  # type: ignore
    assert len(c1[1:]) == 2  # type: ignore
    assert len(c1[0:]) == 3  # type: ignore
    assert len(c1[-3:-1]) == 2  # type: ignore

    assert len(c1[-1]) == 3  # type: ignore

    assert len(c1[[0, 2]]) == 2  # type: ignore
    assert len(c1[[1, 2]]) == 2  # type: ignore
    assert len(c1[[1, -1]]) == 2  # type: ignore
    assert c1[[2, -1]] == c1[[-1, 2]]

    with pytest.raises(AssertionError):
        c1[keys[0]]  # type: ignore

    with pytest.raises(AssertionError):
        c1[range(2)]  # type: ignore

    with pytest.raises(AssertionError):
        c1[[[0]]]  # type: ignore


def test_len(qtbot):
    c1: CustomTableWidget = CustomTableWidget(
        [("a", QWidget), ("b", QLabel)])
    assert len(c1) == 0
    assert len(c1) == len(c1.rows)
    c1.add_row()
    assert len(c1) == 1
    assert len(c1) == len(c1.rows)
    c1.add_row()
    assert len(c1) == 2
    assert len(c1) == len(c1.rows)
    c1.add_row()
    assert len(c1) == 3
    assert len(c1) == len(c1.rows)
    del c1[0]
    assert len(c1) == 2
    assert len(c1) == len(c1.rows)
    c1.add_row()
    c1.add_row()
    assert len(c1) == 4
    assert len(c1) == len(c1.rows)
    del c1[1:]
    assert len(c1) == 1
    assert len(c1) == len(c1.rows)
    del c1[:0]
    assert len(c1) == 1
    assert len(c1) == len(c1.rows)
    del c1[:1]
    assert len(c1) == 0
    assert len(c1) == len(c1.rows)

def test_iter(qtbot):
    c1: CustomTableWidget = CustomTableWidget([("e", QLabel)])
    i = 0
    for _ in c1:
        i += 1
        assert False
    assert 0 == i
    c1.add_row()
    for r in c1:
        i += 1
        assert isinstance(r, Dict)
        assert len(r.keys()) == 1
        assert (list(r.keys())) == ["e"]
        assert isinstance(list(r.values())[0], QLabel)
    assert 1 == i
    c1.add_row()
    c1.add_row()
    i = 0
    for r in c1:
        i += 1
        assert isinstance(r, Dict)
        assert len(r.keys()) == 1
        assert (list(r.keys())) == ["e"]
        assert isinstance(list(r.values())[0], QLabel)
    assert 3 == i

def test_del(qtbot):
    c1: CustomTableWidget = CustomTableWidget(
        [("button", QPushButton), ("button2", QPushButton)])
    with pytest.raises(IndexError):
        del c1[0]
    c1.add_row()
    assert len(c1) == 1
    del c1[0]
    assert len(c1) == 0
    assert c1.main_layout.itemAtPosition(0, 0) is None
    c1.add_row()
    assert len(c1) == 1
    del c1[-1]
    assert len(c1) == 0
    assert c1.main_layout.itemAtPosition(0, 0) is None
    c1.add_row()
    c1.add_row()
    assert len(c1) == 2
    assert c1[(1, "button")].text() == "" # type: ignore
    c1[(1, "button")].setText("text") # type: ignore
    assert c1[(1, "button")].text() == "text" # type: ignore
    del c1[0]
    assert c1[(0, "button")].text() == "text" # type: ignore
    assert len(c1) == 1
    c1.add_row()
    c1.add_row()
    assert len(c1) == 3
    del c1[:]
    assert len(c1) == 0
    assert c1.main_layout.itemAtPosition(0, 0) is None
    c1.add_row()
    c1.add_row()
    c1.add_row()
    assert len(c1) == 3
    assert c1[(0, "button")].text() == "" # type: ignore
    c1[(0, "button")].setText("text") # type: ignore
    assert c1[(0, "button")].text() == "text" # type: ignore
    del c1[1:]
    assert c1[(0, "button")].text() == "text" # type: ignore
    assert len(c1) == 1
    c1.add_row()
    c1.add_row()
    assert len(c1) == 3
    assert c1[(2, "button2")].text() == "" # type: ignore
    c1[(2, "button2")].setText("text2") # type: ignore
    assert c1[(2, "button2")].text() == "text2" # type: ignore
    del c1[:2]
    assert c1[(0, "button2")].text() == "text2" # type: ignore
    assert len(c1) == 1
    c1.add_row()
    c1.add_row()
    c1.add_row()
    assert len(c1) == 4
    assert c1[(3, "button")].text() == "" # type: ignore
    c1[(3, "button")].setText("text3") # type: ignore
    assert c1[(3, "button")].text() == "text3" # type: ignore
    del c1[1:3]
    assert c1[(1, "button")].text() == "text3" # type: ignore
    assert c1[(0, "button2")].text() == "text2" # type: ignore
    assert len(c1) == 2
    c1.insert_row(1)
    assert c1[(2, "button")].text() == "text3" # type: ignore
    c1.add_row()
    assert len(c1) == 4
    del c1[-3:-1]
    assert c1[(0, "button2")].text() == "text2" # type: ignore
    assert c1[(1, "button")].text() == "" # type: ignore
    assert len(c1) == 2
    c1.insert_row(0)
    c1.insert_row(0)
    assert c1[(2, "button2")].text() == "text2" # type: ignore
    assert len(c1) == 4
    del c1[[0, 3, 1]]
    assert c1[(0, "button2")].text() == "text2" # type: ignore
    assert len(c1) == 1
    del c1[[0]]
    assert len(c1) == 0
    assert c1.main_layout.itemAtPosition(0, 0) is None

def test_create_row(qtbot):
    c1: CustomTableWidget = CustomTableWidget()
    r = c1.__create_row()
    assert len(r) == 0
    assert isinstance(r, Dict)
    del r

    c2: CustomTableWidget = CustomTableWidget([("foo", QLabel)])
    r = c2.__create_row()
    assert len(r) == 1
    assert isinstance(r, Dict)
    assert list(r.keys()) == "foo"
    assert isinstance(r["foo"], QWidget)
    del r
