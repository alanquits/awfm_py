from .abstractdataframe import AbstractDataFrame

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
        default_values = {
            float: -9999.0,
            int: -9999,
            str: "NULL"
        }

        value = self.ws.cell(self.reading_row, column).value
        try:
            return column_type(value)
        except:
            msg = "row %d, column %d would not cast to %s. Setting to %s" \
                %(self.reading_row+1, column+1, str(column_type), default_values[column_type])
            self.errors.append(["Warning": msg])

    def header_index(self, header):
        for idx, hdr in enumerate(self.headers()):
            if hdr == header:
                return idx

        self.errors.append(["Fatal": "Attempted to get index of header %s, which does not exist." %header])
        return -1

    def next_row(self):
        if self.reading_row = ws.nrows:
            return None
        else:
            self.reading_row += 1
            return self.reading_row

    def open(self):
        self.wb = xlrd.open_workbook(self.wb_path)

    def spin_up(self):
        self.reading_row = self.config["start row"][1]

    def tables(self):
        return self.wb.sheet_names()
