"""
    tests for CustomTableWidget
"""
from typing import Dict
import pytest

from PySide6.QtWidgets import (  # pylint: disable=import-error
    QWidget,
    QGridLayout,
    QLabel,
    QPushButton,
)

from IPTables_Guide.view.custom_table_widget import CustomTableWidget


def test_initializing(qtbot):
    """
    testing __init__
    """
    _ = qtbot

    # Check default parameeters
    ctw1: CustomTableWidget = CustomTableWidget()
    assert ctw1.row_types == []
    assert ctw1.rows == []
    assert isinstance(ctw1.main_layout, QGridLayout)
    assert ctw1.layout() == ctw1.main_layout
    assert ctw1.main_layout.horizontalSpacing() == 0
    assert ctw1.main_layout.verticalSpacing() == 0
    ctw1.deleteLater()

    # Check giving the same parameters as the default parameeters
    ctw2: CustomTableWidget = CustomTableWidget([], None)
    assert ctw2.row_types == []
    assert ctw2.rows == []
    assert isinstance(ctw2.main_layout, QGridLayout)
    assert ctw2.layout() == ctw2.main_layout
    assert ctw2.main_layout.horizontalSpacing() == 0
    assert ctw2.main_layout.verticalSpacing() == 0
    ctw2.deleteLater()

    # Check non-trivial parameeters
    ctw3: CustomTableWidget = CustomTableWidget([("everything is fabulous", QWidget)])
    assert ctw3.row_types == [("everything is fabulous", QWidget)]
    assert ctw3.rows == []
    assert ctw3.layout() == ctw3.main_layout
    assert isinstance(ctw3.main_layout, QGridLayout)
    assert ctw3.main_layout.horizontalSpacing() == 0
    assert ctw3.main_layout.verticalSpacing() == 0
    ctw3.deleteLater()


def test_getitem(qtbot):
    """
    testing __getitem__
    """
    _ = qtbot

    ctw1: CustomTableWidget = CustomTableWidget(
        [("alpha", QWidget), ("beta", QPushButton), ("gamma", QLabel)]
    )
    ctw1.add_row()
    ctw1.add_row()
    ctw1.add_row()
    keys = ["alpha", "beta", "gamma"]
    types = {}
    for_i = 0
    for key, typ in ctw1.row_types:
        types[key] = typ
        for_i += 1
    assert for_i == len(keys)

    # Check the given keys still the
    assert keys == [k for k, _ in ctw1.row_types]

    # Check all the given rows
    for i in range(3):

        # Check row type
        assert isinstance(ctw1[i], Dict)

        # Check row length
        assert len(ctw1[i]) == 3  # type: ignore

        # Check the keys of the row in an ordered list form
        key_list = list(ctw1[i].keys())  # type: ignore
        key_list.sort()
        assert key_list == keys

        # Check if keys are the same in all the rows
        assert ctw1[i].keys() == ctw1[0].keys()  # type: ignore

        # Check all elements in a row
        for key in keys:

            # Check if it is derived from QWidget
            assert isinstance(ctw1[(i, key)], QWidget)

            # Check if tuple indexing is the same as
            # indexing with the row number and the key
            assert ctw1[i][key] == ctw1[(i, key)]  # type: ignore

            # Check if the given key represent the type given in the constructor
            assert isinstance(ctw1[(i, key)], types[key])

            # Check if the given widget is
            # in the appropriate place in the layout
            assert (
                ctw1[((i, key))]
                == ctw1.main_layout.itemAtPosition(i, keys.index(key)).widget()
            )

    # Check the length of given slice
    assert len(ctw1[:2]) == 2  # type: ignore
    assert len(ctw1[:3]) == 3  # type: ignore
    assert len(ctw1[2:3]) == 1  # type: ignore
    assert len(ctw1[1:2]) == 1  # type: ignore
    assert len(ctw1[0:2]) == 2  # type: ignore
    assert len(ctw1[1:]) == 2  # type: ignore
    assert len(ctw1[0:]) == 3  # type: ignore
    assert len(ctw1[-3:-1]) == 2  # type: ignore

    # Check indexing with slice is the same as indexing with int
    assert ctw1[:2] == [ctw1[0]] + [ctw1[1]]
    assert ctw1[:3] == ctw1[:]
    assert ctw1[2:3] == [ctw1[2]]
    assert ctw1[1:] == [ctw1[1]] + [ctw1[2]]
    assert ctw1[-3:-1] == [ctw1[0]] + [ctw1[1]]

    # Check negative index
    assert len(ctw1[-1]) == 3  # type: ignore

    # Check indexing with list
    assert len(ctw1[[0, 2]]) == 2  # type: ignore
    assert len(ctw1[[1, 2]]) == 2  # type: ignore
    assert len(ctw1[[1, -1]]) == 2  # type: ignore
    assert ctw1[[2, -1]] == ctw1[[-1, 2]]

    # Check indexing with string raises error
    with pytest.raises(AssertionError):
        _ = ctw1[keys[0]]  # type: ignore

    # Check indexing with range raises error
    with pytest.raises(AssertionError):
        _ = ctw1[range(2)]  # type: ignore

    # Check indexing with list of list of int raises error
    with pytest.raises(AssertionError):
        _ = ctw1[[[0]]]  # type: ignore


def test_len(qtbot):
    """
    testing __len__
    """
    _ = qtbot

    ctw1: CustomTableWidget = CustomTableWidget([("a", QWidget), ("b", QLabel)])

    # Check length of an empty table is 0
    assert len(ctw1) == 0

    # Check if len is the same at the count of the rows
    assert len(ctw1) == len(ctw1.rows)

    # Check if adding rows increases the lenght
    ctw1.add_row()
    assert len(ctw1) == 1
    assert len(ctw1) == len(ctw1.rows)
    ctw1.add_row()
    assert len(ctw1) == 2
    assert len(ctw1) == len(ctw1.rows)
    ctw1.add_row()
    assert len(ctw1) == 3
    assert len(ctw1) == len(ctw1.rows)

    # Check deleting a row decrease the lenght
    del ctw1[0]
    assert len(ctw1) == 2
    assert len(ctw1) == len(ctw1.rows)

    # Check if adding row after deleting increases the lenght
    ctw1.add_row()
    ctw1.add_row()
    assert len(ctw1) == 4
    assert len(ctw1) == len(ctw1.rows)

    # Check deleting multiple rows affects the length
    del ctw1[1:]
    assert len(ctw1) == 1
    assert len(ctw1) == len(ctw1.rows)

    # Check deleting the no row leaves the length the same
    del ctw1[:0]
    assert len(ctw1) == 1
    assert len(ctw1) == len(ctw1.rows)

    # Check deleting the only row modify the length to 0
    del ctw1[:1]
    assert len(ctw1) == 0
    assert len(ctw1) == len(ctw1.rows)


def test_iter(qtbot):
    """
    testing __iter__
    """
    _ = qtbot

    ctw1: CustomTableWidget = CustomTableWidget([("e", QLabel)])

    # Check the empty table does not iter
    for_i = 0
    for _ in ctw1:
        for_i += 1
        assert False
    assert for_i == 0

    # Check one row table iter only once with the corresponding values
    ctw1.add_row()
    for row in ctw1:
        for_i += 1
        assert isinstance(row, Dict)
        assert len(row.keys()) == 1
        assert (list(row.keys())) == ["e"]
        assert isinstance(list(row.values())[0], QLabel)
    assert for_i == 1

    # Check iter table with multiple rows
    ctw1.add_row()
    ctw1.add_row()
    for_i = 0
    for row in ctw1:
        for_i += 1
        assert isinstance(row, Dict)
        assert len(row.keys()) == 1
        assert (list(row.keys())) == ["e"]
        assert isinstance(list(row.values())[0], QLabel)
    assert for_i == 3


def test_del(qtbot):  # pylint: disable=R0915
    """
    testing __delitem__
    """
    _ = qtbot

    ctw1: CustomTableWidget = CustomTableWidget(
        [("button", QPushButton), ("button2", QPushButton)]
    )

    # Check deleting an element from an empty table raises an error
    with pytest.raises(IndexError):
        del ctw1[0]

    # Check adding a row and deleting it will ensure an empt table
    ctw1.add_row()
    assert len(ctw1) == 1
    assert ctw1.main_layout.itemAtPosition(0, 0) is not None
    del ctw1[0]
    assert len(ctw1) == 0
    assert ctw1.main_layout.itemAtPosition(0, 0) is None

    # Check deleting the only row with negative index
    ctw1.add_row()
    assert len(ctw1) == 1
    assert ctw1.main_layout.itemAtPosition(0, 0) is not None
    del ctw1[-1]
    assert len(ctw1) == 0
    assert ctw1.main_layout.itemAtPosition(0, 0) is None

    # Check deleint the first row will shift all the rows -1
    ctw1.add_row()
    ctw1.add_row()
    assert len(ctw1) == 2
    assert ctw1[(1, "button")].text() == ""  # type: ignore
    ctw1[(1, "button")].setText("text")  # type: ignore
    assert ctw1[(1, "button")].text() == "text"  # type: ignore
    del ctw1[0]
    assert ctw1[(0, "button")].text() == "text"  # type: ignore
    assert len(ctw1) == 1

    # Check deleting all the rows with slice
    ctw1.add_row()
    ctw1.add_row()
    assert len(ctw1) == 3
    assert ctw1.main_layout.itemAtPosition(0, 0) is not None
    del ctw1[:]
    assert len(ctw1) == 0
    assert ctw1.main_layout.itemAtPosition(0, 0) is None

    # Check the rows not part of the deleting remains the same
    ctw1.add_row()
    assert ctw1.main_layout.itemAtPosition(0, 0) is not None
    ctw1.add_row()
    ctw1.add_row()
    assert len(ctw1) == 3
    assert ctw1[(0, "button")].text() == ""  # type: ignore
    ctw1[(0, "button")].setText("text")  # type: ignore
    assert ctw1[(0, "button")].text() == "text"  # type: ignore
    del ctw1[1:]
    assert ctw1[(0, "button")].text() == "text"  # type: ignore
    assert len(ctw1) == 1

    # Check deleting specific row and
    # deleting the first rows will ensure the tail shifts to the front
    ctw1.add_row()
    ctw1.add_row()
    assert len(ctw1) == 3
    assert ctw1[(2, "button2")].text() == ""  # type: ignore
    ctw1[(2, "button2")].setText("text2")  # type: ignore
    assert ctw1[(2, "button2")].text() == "text2"  # type: ignore
    del ctw1[:2]
    assert ctw1[(0, "button2")].text() == "text2"  # type: ignore
    assert ctw1[(0, "button")].text() == ""  # type: ignore
    assert len(ctw1) == 1

    # Check deleting the middle of the rows
    ctw1.add_row()
    ctw1.add_row()
    ctw1.add_row()
    assert len(ctw1) == 4
    assert ctw1[(3, "button")].text() == ""  # type: ignore
    ctw1[(3, "button")].setText("text3")  # type: ignore
    assert ctw1[(3, "button")].text() == "text3"  # type: ignore
    del ctw1[1:3]
    assert ctw1[(1, "button")].text() == "text3"  # type: ignore
    assert ctw1[(0, "button2")].text() == "text2"  # type: ignore
    assert len(ctw1) == 2

    # Check deleting the middle of the row with negative indices
    ctw1.insert_row(1)
    assert ctw1[(2, "button")].text() == "text3"  # type: ignore
    ctw1.add_row()
    assert len(ctw1) == 4
    del ctw1[-3:-1]
    assert ctw1[(0, "button2")].text() == "text2"  # type: ignore
    assert ctw1[(1, "button")].text() == ""  # type: ignore
    assert len(ctw1) == 2

    # Check deleting specific rows with list
    ctw1.insert_row(0)
    ctw1.insert_row(0)
    assert ctw1[(2, "button2")].text() == "text2"  # type: ignore
    assert len(ctw1) == 4
    del ctw1[[0, 3, 1]]
    assert ctw1[(0, "button2")].text() == "text2"  # type: ignore
    assert len(ctw1) == 1

    # Check deleting the only row with list
    assert ctw1.main_layout.itemAtPosition(0, 0) is not None
    del ctw1[[0]]
    assert len(ctw1) == 0
    assert ctw1.main_layout.itemAtPosition(0, 0) is None


def test_contains(qtbot):
    """
    testing __contains__
    """
    _ = qtbot

    ctw1: CustomTableWidget = CustomTableWidget(
        [
            ("0", QWidget),
            ("2", QWidget),
            ("4", QWidget),
            ("6", QWidget),
            ("8", QWidget),
        ]
    )

    # Check containing keys
    assert all(k in ctw1 for k, _ in ctw1.row_types)
    assert "0" in ctw1
    assert "2" in ctw1
    assert "4" in ctw1
    assert "6" in ctw1
    assert "8" in ctw1

    # Check not containing key
    assert "1" not in ctw1
    assert "3" not in ctw1
    assert "5" not in ctw1
    assert "7" not in ctw1
    assert "9" not in ctw1
    assert "a" not in ctw1
    assert "b" not in ctw1
    assert "c" not in ctw1
    assert "z" not in ctw1
    assert "foo" not in ctw1
    assert "bar" not in ctw1


def test_get_keys(qtbot):
    """
    testing get_keys
    """
    _ = qtbot

    ctw1: CustomTableWidget = CustomTableWidget()

    # Check the keys of a table with empty row_types
    assert len(ctw1.get_keys()) == 0
    assert isinstance(ctw1.get_keys(), list)
    assert ctw1.get_keys() == []

    # Check add_row does not effect keys
    ctw1.add_row()
    assert len(ctw1.get_keys()) == 0
    assert isinstance(ctw1.get_keys(), list)
    assert ctw1.get_keys() == []

    ctw2: CustomTableWidget = CustomTableWidget(
        [
            ("0", QWidget),
            ("2", QWidget),
            ("4", QWidget),
            ("6", QWidget),
            ("8", QWidget),
        ]
    )

    # Check get keys
    assert len(ctw2.get_keys()) == 5
    assert all(k in ctw2 for k in ctw2.get_keys())
    assert ctw2.get_keys() == ["0", "2", "4", "6", "8"]

    # Check add_row does not effect keys
    ctw2.add_row()
    assert len(ctw2.get_keys()) == 5
    assert all(k in ctw2 for k in ctw2.get_keys())
    assert ctw2.get_keys() == ["0", "2", "4", "6", "8"]


def test_get_column(qtbot):
    """
    testing get_column
    """
    _ = qtbot

    ctw1: CustomTableWidget = CustomTableWidget([("a", QPushButton), ("b", QLabel)])

    # Check empty table does not contain any column
    assert len(ctw1.get_column("a")) == 0
    assert len(ctw1.get_column("b")) == 0
    assert isinstance(ctw1.get_column("a"), list)
    assert isinstance(ctw1.get_column("b"), list)
    assert ctw1.get_column("a") == []
    assert ctw1.get_column("b") == []

    # Check table with multiple rows
    ctw1.add_row()
    ctw1.add_row()
    ctw1.add_row()
    assert isinstance(ctw1.get_column("a"), list)
    assert isinstance(ctw1.get_column("b"), list)
    for i in range(3):
        assert ctw1.get_column("a")[i] == ctw1[(i, "a")]
        assert ctw1.get_column("b")[i] == ctw1[(i, "b")]
    assert len(ctw1.get_column("a")) == 3
    assert len(ctw1.get_column("b")) == 3
    assert all(isinstance(w, QPushButton) for w in ctw1.get_column("a"))
    assert all(isinstance(w, QLabel) for w in ctw1.get_column("b"))

    # Check the order of the result
    ctw1[(0, "a")].setText("foo")  # type: ignore
    ctw1[(2, "a")].setText("bar")  # type: ignore
    assert ctw1.get_column("a")[0].text() == "foo"  # type: ignore
    assert ctw1.get_column("a")[1].text() == ""  # type: ignore
    assert ctw1.get_column("a")[2].text() == "bar"  # type: ignore
    assert all(w.text() == "" for w in ctw1.get_column("b"))  # type: ignore


def test_create_row(qtbot):
    """
    testing __create_row
    """
    _ = qtbot

    ctw1: CustomTableWidget = CustomTableWidget()

    # Check creating a row does not result in a new row
    row = ctw1.__create_row()  # pylint: disable=W0212
    assert len(ctw1) == 0

    # Check the new row contains all the element
    # given in the constrictor parameter
    assert len(row) == 0

    # Check the type of the new row
    assert isinstance(row, Dict)
    del row

    ctw2: CustomTableWidget = CustomTableWidget([("foo", QLabel)])

    # Check creating a row does not result in a new row
    row = ctw2.__create_row()  # pylint: disable=W0212
    assert len(ctw1) == 0

    # Check the new row contains all the element
    # given in the constrictor parameter
    assert len(row) == 1

    # Check the type of the new row
    assert isinstance(row, Dict)

    # Check the keys of the new row
    assert list(row.keys()) == ["foo"]

    # Check the row contains widgets
    assert isinstance(row["foo"], QWidget)
    del row


def test_add_row(qtbot):
    """
    testing add_row
    """
    _ = qtbot

    ctw1: CustomTableWidget = CustomTableWidget()

    # Check adding a row rises the length
    assert len(ctw1) == 0
    assert ctw1.main_layout.itemAtPosition(0, 0) is None
    ctw1.add_row()
    assert len(ctw1) == 1
    assert ctw1.main_layout.itemAtPosition(0, 0) is None

    ctw2: CustomTableWidget = CustomTableWidget(
        [("epsilon", QPushButton), ("delta", QLabel)]
    )

    # Check adding a row rises the length and insert the widgets to the layout
    assert len(ctw2) == 0
    assert ctw2.main_layout.itemAtPosition(0, 0) is None
    ctw2.add_row()
    assert len(ctw2) == 1
    assert ctw2.main_layout.itemAtPosition(0, 0) is not None

    # Check the widgets in the layout is in the prefered order
    assert ctw2.main_layout.itemAtPosition(0, 0).widget() == ctw2[(0, "epsilon")]
    assert ctw2.main_layout.itemAtPosition(0, 1).widget() == ctw2[(0, "delta")]


def test_insert_row(qtbot):
    """
    testing insert_row
    """
    _ = qtbot

    ctw1: CustomTableWidget = CustomTableWidget()

    # Check inserting a row to an empy table
    assert len(ctw1) == 0
    ctw1.insert_row(0)
    assert len(ctw1) == 1
    del ctw1[0]

    # Check inserting a row to an empty table
    # with negative index raises an error
    with pytest.raises(AssertionError):
        ctw1.insert_row(-1)

    ctw2: CustomTableWidget = CustomTableWidget([("text", QLabel)])

    # Check inserting a row to the first place shifts the rows down
    ctw2.add_row()
    ctw2.add_row()
    ctw2[(0, "text")].setText("1")  # type: ignore
    ctw2[(1, "text")].setText("2")  # type: ignore
    ctw2.insert_row(0)
    assert ctw2[(0, "text")].text() == ""  # type: ignore
    assert ctw2[(1, "text")].text() == "1"  # type: ignore
    assert ctw2[(2, "text")].text() == "2"  # type: ignore

    # Check insert a row after the last row leave the other rows in place
    ctw2[(0, "text")].setText("0")  # type: ignore
    ctw2.insert_row(3)
    assert ctw2[(0, "text")].text() == "0"  # type: ignore
    assert ctw2[(1, "text")].text() == "1"  # type: ignore
    assert ctw2[(2, "text")].text() == "2"  # type: ignore

    del ctw2[-1]

    # Check inserting a row in the middle of the rows
    ctw2.insert_row(1)
    assert ctw2[(0, "text")].text() == "0"  # type: ignore
    assert ctw2[(1, "text")].text() == ""  # type: ignore
    assert ctw2[(2, "text")].text() == "1"  # type: ignore
    assert ctw2[(3, "text")].text() == "2"  # type: ignore

    del ctw2[1]

    # Check inserting a row in the middle of the rows with negative index
    ctw2.insert_row(-1)
    assert ctw2[(0, "text")].text() == "0"  # type: ignore
    assert ctw2[(1, "text")].text() == "1"  # type: ignore
    assert ctw2[(2, "text")].text() == ""  # type: ignore
    assert ctw2[(3, "text")].text() == "2"  # type: ignore

    # Check overindexing
    with pytest.raises(AssertionError):
        ctw2.insert_row(5)

    # Check underindexing
    with pytest.raises(AssertionError):
        ctw2.insert_row(-5)


def test_apply_method_to_row(qtbot):  # pylint: disable=R0915

    """
    testing apply_method_to_row
    """
    _ = qtbot

    ctw1: CustomTableWidget = CustomTableWidget(
        [("label", QLabel), ("button", QPushButton)]
    )

    # Check apply method effects all the elements in a row indexed with int
    ctw1.add_row()
    for_i = 0
    for key in ctw1[0]:  # type: ignore
        assert ctw1[(0, key)].text() == ""  # type: ignore
        for_i += 1
    assert for_i > 0
    ctw1.apply_method_to_row(0, lambda x: x.setText("foo"))  # type: ignore
    for_i = 0
    for key in ctw1[0]:  # type: ignore
        assert ctw1[(0, key)].text() == "foo"  # type: ignore
        for_i += 1
    assert for_i > 0

    # Check apply method effects all the elements in a row
    # indexed with negative index
    for_i = 0
    for key in ctw1[0]:  # type: ignore
        assert ctw1[(0, key)].text() == "foo"  # type: ignore
        for_i += 1
    assert for_i > 0
    ctw1.apply_method_to_row(-1, lambda x: x.setText("bar"))  # type: ignore
    for_i = 0
    for key in ctw1[0]:  # type: ignore
        assert ctw1[(0, key)].text() == "bar"  # type: ignore
        for_i += 1
    assert for_i > 0

    # Check apply method effects all the elements and no more
    # in a row indexed with slice
    ctw1.add_row()
    ctw1.add_row()
    ctw1.add_row()
    for_i = 0
    for key in ctw1[0]:  # type: ignore
        for row in ctw1:  # type: ignore
            assert row[key].isEnabled() is True  # type: ignore
            for_i += 1
    assert for_i > 0
    ctw1.apply_method_to_row(slice(1, 3), lambda x: x.setEnabled(False))  # type: ignore
    for_i = 0
    for key in ctw1[0]:  # type: ignore
        for row in ctw1[1:3]:  # type: ignore
            assert row[key].isEnabled() is False  # type: ignore
            for_i += 1
        assert ctw1[(0, key)].isEnabled() is True  # type: ignore
        assert ctw1[(3, key)].isEnabled() is True  # type: ignore
    assert for_i > 0

    # Check apply method effects all the elements and no more
    # in a row indexed with negative slice
    for_i = 0
    for key in ctw1[0]:  # type: ignore
        for row in ctw1:
            assert row[key].acceptDrops() is False  # type: ignore
            for_i += 1
    assert for_i > 0
    ctw1.apply_method_to_row(
        slice(-3, -1), lambda x: x.setAcceptDrops(True)
    )  # type: ignore
    for_i = 0
    for_j = 0
    for key in ctw1[0]:  # type: ignore
        for row in ctw1[-3:-1]:  # type: ignore
            assert row[key].acceptDrops() is True  # type: ignore
            for_i += 1
        assert ctw1[(0, key)].acceptDrops() is False  # type: ignore
        assert ctw1[(3, key)].acceptDrops() is False  # type: ignore
        for row in ctw1[1:3]:  # type: ignore
            assert row[key].isEnabled() is False  # type: ignore
            for_j += 1
        assert ctw1[(0, key)].isEnabled() is True  # type: ignore
        assert ctw1[(3, key)].isEnabled() is True  # type: ignore
    assert for_i > 0 and for_j > 0

    del ctw1[:]

    # Check apply method effects all the elements and no more
    # in a row indexed with list
    ctw1.add_row()
    ctw1.add_row()
    ctw1.add_row()
    ctw1.add_row()
    for_i = 0
    for key in ctw1[0]:  # type: ignore
        for row in ctw1:  # type: ignore
            assert row[key].isEnabled() is True  # type: ignore
            for_i += 1
    assert for_i > 0
    ctw1.apply_method_to_row([1, -1], lambda x: x.setEnabled(False))  # type: ignore
    for_i = 0
    for key in ctw1[0]:  # type: ignore
        for row in ctw1[[1, 3]]:  # type: ignore
            assert row[key].isEnabled() is False  # type: ignore
            for_i += 1
        assert ctw1[(0, key)].isEnabled() is True  # type: ignore
        assert ctw1[(2, key)].isEnabled() is True  # type: ignore
    assert for_i > 0


def test_apply_method_to_column(qtbot):
    """
    testing apply_method_to_column
    """
    _ = qtbot

    ctw1: CustomTableWidget = CustomTableWidget([("1", QPushButton), ("2", QWidget)])

    # Check applying a method to a column affects the column and no more
    ctw1.add_row()
    ctw1.add_row()
    ctw1.add_row()
    ctw1.add_row()
    keys = ctw1.get_keys()
    for_i = 0
    for row in ctw1:
        for key in keys:
            assert row[key].isEnabled() is True
            for_i += 1
    assert for_i == 8
    ctw1.apply_method_to_column("1", lambda w: w.setEnabled(False))
    for_i = 0
    for row in ctw1:
        for key in keys:
            assert row[key].isEnabled() == (key != "1")
            for_i += 1
    assert for_i == 8
