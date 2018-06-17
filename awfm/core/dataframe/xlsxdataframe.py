from .abstractdataframe import AbstractDataframe

class XlsxDataframe(AbstractDataframe):
    def __init__(self, infile):
        self.wb_path = infile
        self.wb = None
        self.ws = None
        self.config = self.default_config()
        self.reading_row = None

    def close(self):
        # Resource will release itself (I think)
        pass

    def default_config(self):
        return {
            "header row": [int, 0],
            "start row": [int, 1]
        }

    def get_value(self, column, column_type):
        value = self.ws.cell(self.reading_row, column).value
        try:
            return column_type(value)
        except:
            default = self.default_value_for_type(column_type)
            msg = "row %d, column %d would not cast to %s. Setting to %s" \
                %(self.reading_row+1, column+1, str(column_type), str(default))
            self.errors.append(["Warning", msg])

    def next_row(self):
        if self.reading_row == ws.nrows:
            return None
        else:
            self.reading_row += 1
            return self.reading_row

    def open(self):
        self.wb = xlrd.open_workbook(self.wb_path)

    def spin_up(self):
        self.reading_row = self.config["start row"][1]

    def set_table(self, table_name):
        self.ws = wb.sheet_by_name(table_name)

    def tables(self):
        return self.wb.sheet_names()
