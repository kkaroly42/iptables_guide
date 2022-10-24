"""
    CustomTableWidget supported by Qt
"""
from typing import Callable, Dict, Iterator, List, Optional, TypeAlias, Union, Tuple

# from PySide6.QtCore import Qt
from PySide6.QtWidgets import (  # pylint: disable=import-error
    QWidget,
    QGridLayout,
)  # pylint: disable=import-error

Row: TypeAlias = Dict[str, QWidget]


class CustomTableWidget(QWidget):
    """
        Custom table representation which allows
        to have buttons, checkboxes, etc. in a row
    """

    def __init__(
        self,
        row_types: Optional[List[Tuple[str, type]]] = None,
        parent: Optional[QWidget] = None,
    ):
        """
            row_types: a list containing the key-type values of a row\\
            the elements of the row will be ordered the same way as represented
            in this list

            parent: the containing widget
        """
        super().__init__(parent)
        if row_types is None:
            row_types = []
        assert all(issubclass(t, QWidget) for _, t in row_types)
        self.row_types: List[Tuple[str, type]] = row_types
        self.rows: List[Row] = []
        self.main_layout: QGridLayout = QGridLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setHorizontalSpacing(0)
        self.main_layout.setVerticalSpacing(0)

    # TODO is this necessary?
    # TODO potencial bug source !!!
    # def __setitem__(self, ind_id, value) -> None:
    #     assert isinstance(ind_id, tuple) and len(ind_id) == 2
    #     ind, id = ind_id
    #     self.rows[ind][id] = value

    # TODO indexing with string return column
    # TODO Column type as List of QWidgets
    def __getitem__(
        self, ind_id: Union[int, slice, List[int], Tuple[int, str]]
    ) -> Union[QWidget, List[Row], Row]:
        """
            return the `ind_id` row if `ind_id` is an int, slice or list

            return the `id` widget in the `ind`th row, if `ind_id`
            is a tuple containing (`ind, id`)
        """
        if isinstance(ind_id, tuple):
            assert len(ind_id) == 2
            return self.rows[ind_id[0]][ind_id[1]]
        if isinstance(ind_id, (int, slice)):
            return self.rows[ind_id]  # type: ignore
        if isinstance(ind_id, List) and all(isinstance(i, int) for i in ind_id):
            return [self.rows[i] for i in ind_id]
        assert False

    def __len__(self) -> int:
        """
            return the column count of the table
        """
        return len(self.rows)

    def __iter__(self) -> Iterator:
        """
            return an interator over the rows of the table
        """
        for row in self.rows:
            yield row

    def __delitem__(self, ind: Union[int, slice, List[int]]):
        """
            delete the `ind`th row of the table
        """

        def correct_layout(i):
            for r_ind in range(i + 1, len(self)):
                for c_ind in range(len(self.row_types)):
                    item = self.main_layout.itemAtPosition(r_ind, c_ind)
                    widget: QWidget = item.widget()
                    self.main_layout.addWidget(widget, r_ind - 1, c_ind)
            for widget in self.rows[i].values():
                self.main_layout.removeWidget(widget)
                widget.deleteLater()

        if isinstance(ind, int):
            if ind < 0:
                ind += len(self)
            assert ind >= 0
            correct_layout(ind)
            del self.rows[ind]
        elif isinstance(ind, slice):
            # if ind.start is not None:
            #     if ind.stop is None:
            #         inter = range(ind.start, len(self), ind.step)
            #     else:
            #         inter = range(ind.start, ind.stop, ind.step)
            # else:
            #     inter = range(ind.stop)
            # inter = list(inter)
            inter = list(range(len(self))[ind])
            inter.reverse()
            for i in inter:
                correct_layout(i)
                del self.rows[i]
        elif isinstance(ind, List):
            ind.sort(reverse=True)
            for i in ind:
                correct_layout(i)
                del self.rows[i]
        else:
            assert False

    def __contains__(self, key: str) -> bool:
        """
            return if the table has a column indexed with `key`
        """
        return any(k == key for k, _ in self.row_types)

    def get_keys(self) -> List[str]:
        """
            return the keys of the columns
        """
        return [k for k, _ in self.row_types]

    def get_column(self, col_id: str) -> List[QWidget]:
        """
            return the column represented by `col_id`
        """
        assert col_id in self
        return [r[col_id] for r in self.rows]

    def __create_row(self) -> Row:
        """
            creates a new row, but not insert it
        """
        new_row = {}
        for key, typ in self.row_types:
            new_row[key] = typ(self)
        return new_row

    def add_row(self) -> None:
        """
            append a row to the bottom of the table
        """
        row_count: int = len(self)
        new_row: Row = self.__create_row()
        for i, (k, _) in enumerate(self.row_types):
            self.main_layout.addWidget(new_row[k], row_count, i)
        self.rows.append(new_row)

    def insert_row(self, ind: int) -> None:
        """
            inserts a row before the given index
        """
        row_count: int = len(self)
        if ind < 0:
            ind += row_count
        assert 0 <= ind <= row_count
        new_row: Row = self.__create_row()
        for i, (k, _) in enumerate(self.row_types):
            if ind < row_count:
                for j in range(ind, row_count):
                    widget: QWidget = self.main_layout.itemAtPosition(j, i).widget()
                    self.main_layout.addWidget(widget, j + 1, i)
            self.main_layout.addWidget(new_row[k], ind, i)
        self.rows.insert(ind, new_row)

    def apply_method_to_row(
        self, ind: Union[int, slice, List[int]], func: Callable[[QWidget], None]
    ) -> None:
        """
            apply a method to all the rows at `ind`
        """

        def apply_method_to_widgets(row):
            for widget in row.values():
                func(widget)

        if isinstance(ind, int):
            apply_method_to_widgets(self.rows[ind])
        elif isinstance(ind, slice):
            for row in self.rows[ind]:
                apply_method_to_widgets(row)
        elif isinstance(ind, List):
            assert isinstance(ind[0], int)
            for i in ind:
                apply_method_to_widgets(self.rows[i])
        else:
            assert False

    def apply_method_to_column(
        self, col_id: str, func: Callable[[QWidget], None]
    ) -> None:
        """
            apply a method to the column represented by `col_id`
        """
        for row in self.rows:
            func(row[col_id])
