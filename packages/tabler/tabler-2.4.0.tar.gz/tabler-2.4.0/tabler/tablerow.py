"""Provides the TableRow class.

TableRow provides methods for working with rows in :class:`tabler.Table`
instances.
"""


class TableRow:
    """Provide methods for rows in :class:`tabler.Table` instances."""

    def __init__(self, row, header):
        """Instansiate :class:`TableRow`.

        :param list row: Data stored in this row.
        :param list header: Column headers from table.
        """
        self.row = row
        self.header = header
        self.headers = {}

        for column in self.header:
            self.headers[column] = self.header.index(column)

    def __iter__(self):
        for item in self.row:
            yield item

    def __getitem__(self, index):
        if type(index) == int:
            return self.row[index]
        elif type(index) == str:
            return self.row[self.headers[index]]

    def __setitem__(self, key, item):
        if type(key) == int:
            self.row[key] = item
        elif type(key) == str:
            self.row[self.headers[key]] = item

    def __str__(self):
        return ", ".join((str(cell) for cell in self.row))

    def __len__(self):
        return len(self.row)

    def remove_column(self, column):
        """Remove the passed column.

        :param str column: Header for column to be removed.
        :raises: ValueError: If column is not a valid column header.
        """
        column_index = self.header.index(column)
        self.row.pop(column_index)
        header = list(self.header)
        header.pop(header.index(column))
        self.header = tuple(header)

    def copy(self):
        """Return duplicate tabler.tablerow.TableRow object.

        :rtype: :class:`tabler.tablerow.TableRow`.
        """
        return TableRow(self.row, self.header)
