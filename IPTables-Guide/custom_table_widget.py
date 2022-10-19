from typing import Dict, List, Optional, Union, Tuple, NoReturn

from PySide6.QtWidgets import QWidget, QGridLayout


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
        self.row_types = row_types
        self.rows: List[Dict] = []
        self.setLayout(QGridLayout(self))
        self.layout().setHorizontalSpacing(0)
        self.layout().setVerticalSpacing(0)

    def __setitem__(self, ind_id, value) -> NoReturn:
        assert isinstance(ind_id, tuple) and len(ind_id) == 2
        ind, id = ind_id
        self.rows[ind][id] = value

    def __getitem__(self, ind_id) -> Union[QWidget, Dict[str, QWidget]]:
        if isinstance(ind_id, tuple):
            assert len(ind_id) == 2
            ind, id = ind_id
            return self.rows[ind][id]
        elif isinstance(ind_id, (int, slice)):
            return self.rows[ind_id]
        else:
            assert False

    def __len__(self) -> int:
        return len(self.rows)

    def __iter__(self):
        for row in self.rows:
            yield row

    def __create_row(self) -> Dict[str, QWidget]:
        """
            creates a new row, but not insert it
        """
        new_row = {}
        for k, t in self.row_types:
            new_row[k] = t(self)
        return new_row

    def add_row(self):
        row_count = len(self)
        new_row = self.__create_row()
        for i, (k, t) in enumerate(self.row_types):
            self.layout().addWidget(new_row[k], row_count, i)
        self.rows.append(new_row)

    def delete_row(self, ind: Union[int, slice]):
        def remove_and_delete_widgets(row_i):
            for w in self.rows[row_i].values():
                w.deleteLater()
        if isinstance(ind, int):
            remove_and_delete_widgets(ind)
        elif isinstance(ind, slice):
            for i in slice:
                remove_and_delete_widgets(i)
        del self.rows[ind]

    def insert_row(self, ind: int):
        row_count = len(self)
        if ind < 0:
            ind = row_count + ind
        assert 0 <= ind and ind <= row_count
        new_row = self.__create_row()
        for i, (k, _) in enumerate(self.row_types):
            if ind < row_count:
                for j in range(ind, row_count):
                    w = self.layout().itemAtPosition(j, i).widget()
                    self.layout().addWidget(w, j + 1, i)
            self.layout().addWidget(new_row[k], ind, i)
        self.rows.insert(ind, new_row)
