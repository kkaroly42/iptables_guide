from typing import Dict
from custom_table_widget import CustomTableWidget, Row

from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton
import pytest


def test_initializing(qtbot):
    # Check default parameeters
    c1: CustomTableWidget = CustomTableWidget()
    assert c1.row_types == []
    assert c1.rows == []
    assert isinstance(c1.main_layout, QGridLayout)
    assert c1.layout() == c1.main_layout
    assert c1.main_layout.horizontalSpacing() == 0
    assert c1.main_layout.verticalSpacing() == 0
    c1.deleteLater()

    # Check giving the same parameters as the default parameeters
    c2: CustomTableWidget = CustomTableWidget([], None)
    assert c2.row_types == []
    assert c2.rows == []
    assert isinstance(c2.main_layout, QGridLayout)
    assert c2.layout() == c2.main_layout
    assert c2.main_layout.horizontalSpacing() == 0
    assert c2.main_layout.verticalSpacing() == 0
    c2.deleteLater()

    # Check non-trivial parameeters
    c3: CustomTableWidget = CustomTableWidget([("everything is fabulous", QWidget)])
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
    for_i = 0
    for k, t in c1.row_types:
        types[k] = t
        for_i += 1
    assert for_i == len(keys)

    # Check the given keys still the
    assert keys == [k for k, _ in c1.row_types]

    # Check all the given rows
    for i in range(3):

        # Check row type
        assert isinstance(c1[i], Dict)

        # Check row length
        assert len(c1[i]) == 3  # type: ignore

        # Check the keys of the row in an ordered list form
        l = list(c1[i].keys())  # type: ignore
        l.sort()
        assert l == keys

        # Check if keys are the same in all the rows
        assert c1[i].keys() == c1[0].keys()  # type: ignore

        # Check all elements in a row
        for k in keys:

            # Check if it is derived from QWidget
            assert isinstance(c1[(i, k)], QWidget)

            # Check if tuple indexing is the same as
            # indexing with the row number and the key
            assert c1[i][k] == c1[(i, k)]  # type: ignore

            # Check if the given key represent the type given in the constructor
            assert isinstance(c1[(i, k)], types[k])

            # Check if the given widget is
            # in the appropriate place in the layout
            assert (
                c1[((i, k))] == c1.main_layout.itemAtPosition(i, keys.index(k)).widget()
            )

    # Check the length of given slice
    assert len(c1[:2]) == 2  # type: ignore
    assert len(c1[:3]) == 3  # type: ignore
    assert len(c1[2:3]) == 1  # type: ignore
    assert len(c1[1:2]) == 1  # type: ignore
    assert len(c1[0:2]) == 2  # type: ignore
    assert len(c1[1:]) == 2  # type: ignore
    assert len(c1[0:]) == 3  # type: ignore
    assert len(c1[-3:-1]) == 2  # type: ignore

    # Check indexing with slice is the same as indexing with int
    assert c1[:2] == [c1[0]] + [c1[1]]
    assert c1[:3] == c1[:]
    assert c1[2:3] == [c1[2]]
    assert c1[1:] == [c1[1]] + [c1[2]]
    assert c1[-3:-1] == [c1[0]] + [c1[1]]

    # Check negative index
    assert len(c1[-1]) == 3  # type: ignore

    # Check indexing with list
    assert len(c1[[0, 2]]) == 2  # type: ignore
    assert len(c1[[1, 2]]) == 2  # type: ignore
    assert len(c1[[1, -1]]) == 2  # type: ignore
    assert c1[[2, -1]] == c1[[-1, 2]]

    # Check indexing with string raises error
    with pytest.raises(AssertionError):
        c1[keys[0]]  # type: ignore

    # Check indexing with range raises error
    with pytest.raises(AssertionError):
        c1[range(2)]  # type: ignore

    # Check indexing with list of list of int raises error
    with pytest.raises(AssertionError):
        c1[[[0]]]  # type: ignore


def test_len(qtbot):
    c1: CustomTableWidget = CustomTableWidget([("a", QWidget), ("b", QLabel)])

    # Check length of an empty table is 0
    assert len(c1) == 0

    # Check if len is the same at the count of the rows
    assert len(c1) == len(c1.rows)

    # Check if adding rows increases the lenght
    c1.add_row()
    assert len(c1) == 1
    assert len(c1) == len(c1.rows)
    c1.add_row()
    assert len(c1) == 2
    assert len(c1) == len(c1.rows)
    c1.add_row()
    assert len(c1) == 3
    assert len(c1) == len(c1.rows)

    # Check deleting a row decrease the lenght
    del c1[0]
    assert len(c1) == 2
    assert len(c1) == len(c1.rows)

    # Check if adding row after deleting increases the lenght
    c1.add_row()
    c1.add_row()
    assert len(c1) == 4
    assert len(c1) == len(c1.rows)

    # Check deleting multiple rows affects the length
    del c1[1:]
    assert len(c1) == 1
    assert len(c1) == len(c1.rows)

    # Check deleting the no row leaves the length the same
    del c1[:0]
    assert len(c1) == 1
    assert len(c1) == len(c1.rows)

    # Check deleting the only row modify the length to 0
    del c1[:1]
    assert len(c1) == 0
    assert len(c1) == len(c1.rows)


def test_iter(qtbot):
    c1: CustomTableWidget = CustomTableWidget([("e", QLabel)])

    # Check the empty table does not iter
    for_i = 0
    for _ in c1:
        for_i += 1
        assert False
    assert 0 == for_i

    # Check one row table iter only once with the corresponding values
    c1.add_row()
    for r in c1:
        for_i += 1
        assert isinstance(r, Dict)
        assert len(r.keys()) == 1
        assert (list(r.keys())) == ["e"]
        assert isinstance(list(r.values())[0], QLabel)
    assert 1 == for_i

    # Check iter table with multiple rows
    c1.add_row()
    c1.add_row()
    for_i = 0
    for r in c1:
        for_i += 1
        assert isinstance(r, Dict)
        assert len(r.keys()) == 1
        assert (list(r.keys())) == ["e"]
        assert isinstance(list(r.values())[0], QLabel)
    assert 3 == for_i


def test_del(qtbot):
    c1: CustomTableWidget = CustomTableWidget(
        [("button", QPushButton), ("button2", QPushButton)]
    )

    # Check deleting an element from an empty table raises an error
    with pytest.raises(IndexError):
        del c1[0]

    # Check adding a row and deleting it will ensure an empt table
    c1.add_row()
    assert len(c1) == 1
    assert c1.main_layout.itemAtPosition(0, 0) is not None
    del c1[0]
    assert len(c1) == 0
    assert c1.main_layout.itemAtPosition(0, 0) is None

    # Check deleting the only row with negative index
    c1.add_row()
    assert len(c1) == 1
    assert c1.main_layout.itemAtPosition(0, 0) is not None
    del c1[-1]
    assert len(c1) == 0
    assert c1.main_layout.itemAtPosition(0, 0) is None

    # Check deleint the first row will shift all the rows -1
    c1.add_row()
    c1.add_row()
    assert len(c1) == 2
    assert c1[(1, "button")].text() == ""  # type: ignore
    c1[(1, "button")].setText("text")  # type: ignore
    assert c1[(1, "button")].text() == "text"  # type: ignore
    del c1[0]
    assert c1[(0, "button")].text() == "text"  # type: ignore
    assert len(c1) == 1

    # Check deleting all the rows with slice
    c1.add_row()
    c1.add_row()
    assert len(c1) == 3
    assert c1.main_layout.itemAtPosition(0, 0) is not None
    del c1[:]
    assert len(c1) == 0
    assert c1.main_layout.itemAtPosition(0, 0) is None

    # Check the rows not part of the deleting remains the same
    c1.add_row()
    assert c1.main_layout.itemAtPosition(0, 0) is not None
    c1.add_row()
    c1.add_row()
    assert len(c1) == 3
    assert c1[(0, "button")].text() == ""  # type: ignore
    c1[(0, "button")].setText("text")  # type: ignore
    assert c1[(0, "button")].text() == "text"  # type: ignore
    del c1[1:]
    assert c1[(0, "button")].text() == "text"  # type: ignore
    assert len(c1) == 1

    # Check deleting specific row and
    # deleting the first rows will ensure the tail shifts to the front
    c1.add_row()
    c1.add_row()
    assert len(c1) == 3
    assert c1[(2, "button2")].text() == ""  # type: ignore
    c1[(2, "button2")].setText("text2")  # type: ignore
    assert c1[(2, "button2")].text() == "text2"  # type: ignore
    del c1[:2]
    assert c1[(0, "button2")].text() == "text2"  # type: ignore
    assert c1[(0, "button")].text() == ""  # type: ignore
    assert len(c1) == 1

    # Check deleting the middle of the rows
    c1.add_row()
    c1.add_row()
    c1.add_row()
    assert len(c1) == 4
    assert c1[(3, "button")].text() == ""  # type: ignore
    c1[(3, "button")].setText("text3")  # type: ignore
    assert c1[(3, "button")].text() == "text3"  # type: ignore
    del c1[1:3]
    assert c1[(1, "button")].text() == "text3"  # type: ignore
    assert c1[(0, "button2")].text() == "text2"  # type: ignore
    assert len(c1) == 2

    # Check deleting the middle of the row with negative indices
    c1.insert_row(1)
    assert c1[(2, "button")].text() == "text3"  # type: ignore
    c1.add_row()
    assert len(c1) == 4
    del c1[-3:-1]
    assert c1[(0, "button2")].text() == "text2"  # type: ignore
    assert c1[(1, "button")].text() == ""  # type: ignore
    assert len(c1) == 2

    # Check deleting specific rows with list
    c1.insert_row(0)
    c1.insert_row(0)
    assert c1[(2, "button2")].text() == "text2"  # type: ignore
    assert len(c1) == 4
    del c1[[0, 3, 1]]
    assert c1[(0, "button2")].text() == "text2"  # type: ignore
    assert len(c1) == 1

    # Check deleting the only row with list
    assert c1.main_layout.itemAtPosition(0, 0) is not None
    del c1[[0]]
    assert len(c1) == 0
    assert c1.main_layout.itemAtPosition(0, 0) is None


def test_contains(qtbot):
    c1: CustomTableWidget = CustomTableWidget(
        [
            ("0", QWidget),
            ("2", QWidget),
            ("4", QWidget),
            ("6", QWidget),
            ("8", QWidget),
        ]
    )

    # Check containing keys
    assert all(k in c1 for k, _ in c1.row_types)
    assert "0" in c1
    assert "2" in c1
    assert "4" in c1
    assert "6" in c1
    assert "8" in c1

    # Check not containing key
    assert "1" not in c1
    assert "3" not in c1
    assert "5" not in c1
    assert "7" not in c1
    assert "9" not in c1
    assert "a" not in c1
    assert "b" not in c1
    assert "c" not in c1
    assert "z" not in c1
    assert "foo" not in c1
    assert "bar" not in c1


def test_get_keys(qtbot):
    c1: CustomTableWidget = CustomTableWidget()

    # Check the keys of a table with empty row_types
    assert len(c1.get_keys()) == 0
    assert isinstance(c1.get_keys(), list)
    assert c1.get_keys() == []

    # Check add_row does not effect keys
    c1.add_row()
    assert len(c1.get_keys()) == 0
    assert isinstance(c1.get_keys(), list)
    assert c1.get_keys() == []

    c2: CustomTableWidget = CustomTableWidget(
        [
            ("0", QWidget),
            ("2", QWidget),
            ("4", QWidget),
            ("6", QWidget),
            ("8", QWidget),
        ]
    )

    # Check get keys
    assert len(c2.get_keys()) == 5
    assert all(k in c2 for k in c2.get_keys())
    assert c2.get_keys() == ["0", "2", "4", "6", "8"]

    # Check add_row does not effect keys
    c2.add_row()
    assert len(c2.get_keys()) == 5
    assert all(k in c2 for k in c2.get_keys())
    assert c2.get_keys() == ["0", "2", "4", "6", "8"]


def test_get_column(qtbot):
    c1: CustomTableWidget = CustomTableWidget([("a", QPushButton), ("b", QLabel)])

    # Check empty table does not contain any column
    assert len(c1.get_column("a")) == 0
    assert len(c1.get_column("b")) == 0
    assert isinstance(c1.get_column("a"), list)
    assert isinstance(c1.get_column("b"), list)
    assert c1.get_column("a") == []
    assert c1.get_column("b") == []

    # Check table with multiple rows
    c1.add_row()
    c1.add_row()
    c1.add_row()
    assert isinstance(c1.get_column("a"), list)
    assert isinstance(c1.get_column("b"), list)
    for i in range(3):
        assert c1.get_column("a")[i] == c1[(i, "a")]
        assert c1.get_column("b")[i] == c1[(i, "b")]
    assert len(c1.get_column("a")) == 3
    assert len(c1.get_column("b")) == 3
    assert all(isinstance(w, QPushButton) for w in c1.get_column("a"))
    assert all(isinstance(w, QLabel) for w in c1.get_column("b"))

    # Check the order of the result
    c1[(0, "a")].setText("foo")  # type: ignore
    c1[(2, "a")].setText("bar")  # type: ignore
    assert c1.get_column("a")[0].text() == "foo"  # type: ignore
    assert c1.get_column("a")[1].text() == ""  # type: ignore
    assert c1.get_column("a")[2].text() == "bar"  # type: ignore
    assert all(w.text() == "" for w in c1.get_column("b"))  # type: ignore


def test_create_row(qtbot):
    c1: CustomTableWidget = CustomTableWidget()

    # Check creating a row does not result in a new row
    r = c1.__create_row()
    assert len(c1) == 0

    # Check the new row contains all the element
    # given in the constrictor parameter
    assert len(r) == 0

    # Check the type of the new row
    assert isinstance(r, Dict)
    del r

    c2: CustomTableWidget = CustomTableWidget([("foo", QLabel)])

    # Check creating a row does not result in a new row
    r = c2.__create_row()
    assert len(c1) == 0

    # Check the new row contains all the element
    # given in the constrictor parameter
    assert len(r) == 1

    # Check the type of the new row
    assert isinstance(r, Dict)

    # Check the keys of the new row
    assert list(r.keys()) == ["foo"]

    # Check the row contains widgets
    assert isinstance(r["foo"], QWidget)
    del r


def test_add_row(qtbot):
    c1: CustomTableWidget = CustomTableWidget()

    # Check adding a row rises the length
    assert len(c1) == 0
    assert c1.main_layout.itemAtPosition(0, 0) is None
    c1.add_row()
    assert len(c1) == 1
    assert c1.main_layout.itemAtPosition(0, 0) is None

    c2: CustomTableWidget = CustomTableWidget(
        [("epsilon", QPushButton), ("delta", QLabel)]
    )

    # Check adding a row rises the length and insert the widgets to the layout
    assert len(c2) == 0
    assert c2.main_layout.itemAtPosition(0, 0) is None
    c2.add_row()
    assert len(c2) == 1
    assert c2.main_layout.itemAtPosition(0, 0) is not None

    # Check the widgets in the layout is in the prefered order
    assert c2.main_layout.itemAtPosition(0, 0).widget() == c2[(0, "epsilon")]
    assert c2.main_layout.itemAtPosition(0, 1).widget() == c2[(0, "delta")]


def test_insert_row(qtbot):
    c1: CustomTableWidget = CustomTableWidget()

    # Check inserting a row to an empy table
    assert len(c1) == 0
    c1.insert_row(0)
    assert len(c1) == 1
    del c1[0]

    # Check inserting a row to an empty table
    # with negative index raises an error
    with pytest.raises(AssertionError):
        c1.insert_row(-1)

    c2: CustomTableWidget = CustomTableWidget([("text", QLabel)])

    # Check inserting a row to the first place shifts the rows down
    c2.add_row()
    c2.add_row()
    c2[(0, "text")].setText("1")  # type: ignore
    c2[(1, "text")].setText("2")  # type: ignore
    c2.insert_row(0)
    assert c2[(0, "text")].text() == ""  # type: ignore
    assert c2[(1, "text")].text() == "1"  # type: ignore
    assert c2[(2, "text")].text() == "2"  # type: ignore

    # Check insert a row after the last row leave the other rows in place
    c2[(0, "text")].setText("0")  # type: ignore
    c2.insert_row(3)
    assert c2[(0, "text")].text() == "0"  # type: ignore
    assert c2[(1, "text")].text() == "1"  # type: ignore
    assert c2[(2, "text")].text() == "2"  # type: ignore

    del c2[-1]

    # Check inserting a row in the middle of the rows
    c2.insert_row(1)
    assert c2[(0, "text")].text() == "0"  # type: ignore
    assert c2[(1, "text")].text() == ""  # type: ignore
    assert c2[(2, "text")].text() == "1"  # type: ignore
    assert c2[(3, "text")].text() == "2"  # type: ignore

    del c2[1]

    # Check inserting a row in the middle of the rows with negative index
    c2.insert_row(-1)
    assert c2[(0, "text")].text() == "0"  # type: ignore
    assert c2[(1, "text")].text() == "1"  # type: ignore
    assert c2[(2, "text")].text() == ""  # type: ignore
    assert c2[(3, "text")].text() == "2"  # type: ignore

    # Check overindexing
    with pytest.raises(AssertionError):
        c2.insert_row(5)

    # Check underindexing
    with pytest.raises(AssertionError):
        c2.insert_row(-5)


def test_apply_method_to_row(qtbot):
    c1: CustomTableWidget = CustomTableWidget(
        [("label", QLabel), ("button", QPushButton)]
    )

    # Check apply method effects all the elements in a row indexed with int
    c1.add_row()
    for_i = 0
    for k in c1[0]:  # type: ignore
        assert c1[(0, k)].text() == ""  # type: ignore
        for_i += 1
    assert for_i > 0
    c1.apply_method_to_row(0, lambda x: x.setText("foo"))  # type: ignore
    for_i = 0
    for k in c1[0]:  # type: ignore
        assert c1[(0, k)].text() == "foo"  # type: ignore
        for_i += 1
    assert for_i > 0

    # Check apply method effects all the elements in a row
    # indexed with negative index
    for_i = 0
    for k in c1[0]:  # type: ignore
        assert c1[(0, k)].text() == "foo"  # type: ignore
        for_i += 1
    assert for_i > 0
    c1.apply_method_to_row(-1, lambda x: x.setText("bar"))  # type: ignore
    for_i = 0
    for k in c1[0]:  # type: ignore
        assert c1[(0, k)].text() == "bar"  # type: ignore
        for_i += 1
    assert for_i > 0

    # Check apply method effects all the elements and no more
    # in a row indexed with slice
    c1.add_row()
    c1.add_row()
    c1.add_row()
    for_i = 0
    for k in c1[0]:  # type: ignore
        for r in c1:  # type: ignore
            assert r[k].isEnabled() == True  # type: ignore
            for_i += 1
    assert for_i > 0
    c1.apply_method_to_row(slice(1, 3), lambda x: x.setEnabled(False))  # type: ignore
    for_i = 0
    for k in c1[0]:  # type: ignore
        for r in c1[1:3]:  # type: ignore
            assert r[k].isEnabled() == False  # type: ignore
            for_i += 1
        assert c1[(0, k)].isEnabled() == True  # type: ignore
        assert c1[(3, k)].isEnabled() == True  # type: ignore
    assert for_i > 0

    # Check apply method effects all the elements and no more
    # in a row indexed with negative slice
    for_i = 0
    for k in c1[0]:  # type: ignore
        for r in c1:
            assert r[k].acceptDrops() == False  # type: ignore
            for_i += 1
    assert for_i > 0
    c1.apply_method_to_row(
        slice(-3, -1), lambda x: x.setAcceptDrops(True)
    )  # type: ignore
    for_i = 0
    for_j = 0
    for k in c1[0]:  # type: ignore
        for r in c1[-3:-1]:  # type: ignore
            assert r[k].acceptDrops() == True  # type: ignore
            for_i += 1
        assert c1[(0, k)].acceptDrops() == False  # type: ignore
        assert c1[(3, k)].acceptDrops() == False  # type: ignore
        for r in c1[1:3]:  # type: ignore
            assert r[k].isEnabled() == False  # type: ignore
            for_j += 1
        assert c1[(0, k)].isEnabled() == True  # type: ignore
        assert c1[(3, k)].isEnabled() == True  # type: ignore
    assert for_i > 0 and for_j > 0

    del c1[:]

    # Check apply method effects all the elements and no more
    # in a row indexed with list
    c1.add_row()
    c1.add_row()
    c1.add_row()
    c1.add_row()
    for_i = 0
    for k in c1[0]:  # type: ignore
        for r in c1:  # type: ignore
            assert r[k].isEnabled() == True  # type: ignore
            for_i += 1
    assert for_i > 0
    c1.apply_method_to_row([1, -1], lambda x: x.setEnabled(False))  # type: ignore
    for_i = 0
    for k in c1[0]:  # type: ignore
        for r in c1[[1, 3]]:  # type: ignore
            assert r[k].isEnabled() == False  # type: ignore
            for_i += 1
        assert c1[(0, k)].isEnabled() == True  # type: ignore
        assert c1[(2, k)].isEnabled() == True  # type: ignore
    assert for_i > 0


def test_apply_method_to_column(qtbot):
    c1: CustomTableWidget = CustomTableWidget([("1", QPushButton), ("2", QWidget)])

    # Check applying a method to a column affects the column and no more
    c1.add_row()
    c1.add_row()
    c1.add_row()
    c1.add_row()
    keys = c1.get_keys()
    for_i = 0
    for r in c1:
        for k in keys:
            assert r[k].isEnabled() == True
            for_i += 1
    assert for_i == 8
    c1.apply_method_to_column("1", lambda w: w.setEnabled(False))
    for_i = 0
    for r in c1:
        for k in keys:
            assert r[k].isEnabled() == (k != "1")
            for_i += 1
    assert for_i == 8
