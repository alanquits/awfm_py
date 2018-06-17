from .abstractdataframe import AbstractDataframe
import csv

class DelimitedDataframe(AbstractDataframe):
    def __init__(self, infile):
        super().__init__()
        self.errors = []
        self.config = self.default_config()
        self.infile = infile
        self.current_row_data = []
        self.cached_headers = []
        self.is_spun_up = False

    def default_config(self):
        return {
            "delimiter": ",",
            "quote_char": '"'
        }

    def spin_up(self):
        if not self.is_spun_up:
            self.close()
            self.open()

    def get_value(self, column, column_type):
        value = self.current_row_data[column]
        try:
            return column_type(value)
        except:
            default = self.default_value_for_type(column_type)
            msg = "row %d, column %d would not cast to %s. Setting to %s" \
                %(self.reading_row+1, column+1, str(column_type), str(default))
            self.errors.append(["Warning", msg])

    def headers(self):
        return self.cached_headers

    def next_row(self):
        self.is_spun_up = False
        try:
            self.current_row_data = next(self.csv_reader)
            return True
        except StopIteration:
            return None

    def open(self):
        self.csv_file = open(self.infile, newline='')
        self.csv_reader = csv.reader(self.csv_file, delimiter=self.config["delimiter"], \
                                                    quotechar=self.config["quote_char"])
        if self.next_row():
            self.cached_headers = self.current_row_data
        else:
            self.errors.append(["Warning", "CSV file %s does not appear to contain any data." %self.infile])

        self.is_spun_up = True

    def close(self):
        close(self.csv_file)

    def set_table(self, table_name):
        pass

    def tables(self):
        return [self.infile,]

if __name__ == "__main__":
    df = DelimitedDataframe("test_files/sample.csv")
    df.open()
    print(df.headers())
    while (df.next_row() is not None):
        print(df.current_row_data)
