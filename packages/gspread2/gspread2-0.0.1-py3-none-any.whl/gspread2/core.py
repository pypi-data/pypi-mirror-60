from gspread import utils as _gspread_utils
from . import credentials as _credentials


class Cell:
    def __init__(self, worksheet, row, column, value):
        self._worksheet = worksheet
        self.row = row
        self.column = column
        self._value = value

    def refresh(self):
        return self._worksheet.cell(self.row, self.column)

    def as_formula(self):
        return self._worksheet.cell(self.row, self.column, value_render_option='FORMULA')

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self._worksheet.update_cell(self.row, self.column, self._value)

    @property
    def col(self):
        """Implemented for gspread compatibility"""
        return self.column

    @property
    def coordinates(self):
        return _gspread_utils.rowcol_to_a1(self.row, self.column)

    def __repr__(self):
        return "<Cell '%s'>" % self.coordinates


class Worksheet:
    def __init__(self, gspread_worksheet):
        self._worksheet = gspread_worksheet
        self._cells = []

    def __repr__(self):
        return "<Worksheet '%s'>" % self._worksheet.title

    def __getattr__(self, item):
        try:
            return getattr(self._worksheet, item)
        except AttributeError:
            raise AttributeError("'Worksheet' object has no attribute '%s'" % item)

    @property
    def name(self):
        return self._worksheet.title

    @property
    def id(self):
        return self._worksheet.id

    def cell(self, *args, value_render_option='FORMATTED_VALUE'):
        if len(args) == 1:
            arg = args[0]
            assert isinstance(arg, str)
            cell = self._worksheet.acell(arg, value_render_option=value_render_option)
            return Cell(self, cell.row, cell.col, cell.value)
        assert len(args) == 2
        assert all(isinstance(x, int) for x in args)
        cell = self._worksheet.cell(*args, value_render_option=value_render_option)
        return Cell(self, cell.row, cell.col, cell.value)


class Workbook:
    def __init__(self, url, credentials):
        self.url = url
        self._client = _credentials.authorize(credentials)
        self._workbook = self._client.open_by_url(self.url)

    @property
    def worksheets(self):
        sheets = self._workbook.worksheets()
        for s in sheets:
            yield Worksheet(s)

    @property
    def active(self):
        return self._workbook.sheet1

    def __getitem__(self, item):
        if isinstance(item, int):
            sheet = self._workbook.get_worksheet(item)
            return Worksheet(sheet) if sheet is not None else None
        sheet = self._workbook.worksheet(item)
        return Worksheet(sheet) if sheet is not None else None

    def __getattr__(self, item):
        try:
            return getattr(self._workbook, item)
        except AttributeError:
            raise AttributeError("'Workbook' object has no attribute '%s'" % item)
