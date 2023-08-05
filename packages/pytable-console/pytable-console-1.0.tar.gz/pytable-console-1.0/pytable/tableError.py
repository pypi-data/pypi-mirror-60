class TableError(Exception):
    pass

class TableEmptyError(TableError):
    def __init__(self, msg='The pytable is empty.'):
        super().__init__(msg)

class RowLengthError(TableError):
    def __init__(self, msg='Number of columns does not match current pytable.'):
        super().__init__(msg)

class ColumnLengthError(TableError):
    def __init__(self, msg='Number of rows does not match current pytable.'):
        super().__init__(msg)
