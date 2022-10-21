from typing import Callable, Dict, Iterator, List, Optional, TypeAlias, Union, Tuple, Callable

from PySide6.QtWidgets import QWidget, QGridLayout

Row: TypeAlias = Dict[str, QWidget]


class CustomTableWidget(QWidget):
    """
        Custom table representation which allows
        to have buttons, checkboxes, etc. in a row
    """

    def __init__(
            self,
            row_types: List[Tuple[str, type]] = [],
            parent: Optional[QWidget] = None):
        """
            row_types: a list containing the key-type values of a row\\
            the elements of the row will be ordered the same way as represented
            in this list

            parent: the containing widget
        """
        super(CustomTableWidget, self).__init__(parent)
        assert all(issubclass(t, QWidget) for _, t in row_types)
        self.row_types: List[Tuple[str, type]] = row_types
        self.rows: List[Row] = []
        self.main_layout: QGridLayout = QGridLayout(self)
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
            self,
            ind_id: Union[int, slice, List[int], Tuple[int, str]]
    ) -> Union[QWidget, List[Row], Row]:
        if isinstance(ind_id, tuple):
            assert len(ind_id) == 2
            ind, id = ind_id
            return self.rows[ind][id]
        elif isinstance(ind_id, (int, slice)):
            return self.rows[ind_id]  # type: ignore
        elif isinstance(ind_id, List) and \
                all(isinstance(i, int) for i in ind_id):
            return [self.rows[i] for i in ind_id]
        else:
            assert False

    def __len__(self) -> int:
        return len(self.rows)

    def __iter__(self) -> Iterator:
        for row in self.rows:
            yield row

    def __delitem__(self, ind: Union[int, slice, List[int]]):
        def correct_layout(i):
            for r_ind in range(i, len(self)):
                for c_ind in range(len(self.row_types)):
                    item = self.main_layout.itemAtPosition(r_ind, c_ind)
                    w: QWidget = item.widget()
                    self.main_layout.addWidget(w, r_ind - 1, c_ind)
            for w in self.rows[i].values():
                self.main_layout.removeWidget(w)
                w.deleteLater()

        if isinstance(ind, int):
            if ind < 0:
                ind += len(self)
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
        return any(k == key for k, _ in self.row_types)

    def get_keys(self) -> List[str]:
        return [k for k, _ in self.row_types]

    def get_column(self, id: str) -> List[QWidget]:
        assert id in self
        return [r[id] for r in self.rows]

    def __create_row(self) -> Row:
        """
            creates a new row, but not insert it
        """
        new_row = {}
        for k, t in self.row_types:
            new_row[k] = t(self)
        return new_row

    def add_row(self) -> None:
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
        assert 0 <= ind and ind <= row_count
        new_row: Row = self.__create_row()
        for i, (k, _) in enumerate(self.row_types):
            if ind < row_count:
                for j in range(ind, row_count):
                    w: QWidget = self.main_layout.itemAtPosition(j, i).widget()
                    self.main_layout.addWidget(w, j + 1, i)
            self.main_layout.addWidget(new_row[k], ind, i)
        self.rows.insert(ind, new_row)

    def apply_method_to_row(
        self,
        ind: Union[int, slice, List[int]],
        func: Callable[[QWidget], None]
    ) -> None:
        def apply_method_to_widgets(r):
            for w in r.values():
                func(w)
        if isinstance(ind, int):
            apply_method_to_widgets(self.rows[ind])
        elif isinstance(ind, slice):
            for r in self.rows[ind]:
                apply_method_to_widgets(r)
        elif isinstance(ind, List):
            assert isinstance(ind[0], int)
            for i in ind:
                apply_method_to_widgets(self.rows[i])
        else:
            assert False

    def apply_method_to_column(
        self,
        id: str,
        func: Callable[[QWidget], None]
    ) -> None:
        for r in self.rows:
            func(r[id])
