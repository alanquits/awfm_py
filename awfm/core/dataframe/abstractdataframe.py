from abc import ABC, abstractmethod

class AbstractDataframe(ABC):
    def __init__(self):
        super().__init__()
        self.errors = []

    def default_value_for_type(self, type):
        default_values = {
            float: -9999.0,
            int: -9999,
            str: "NULL"
        }
        return default_values[type]

    def generate_column_lookup(self, named_record_map):
        for dst in named_record_map.keys():
            named_record_map[dst] = self.header_index(named_record_map[dst])
        return named_record_map

    def header_index(self, header):
        for idx, hdr in enumerate(self.headers()):
            if hdr == header:
                return idx

        self.errors.append(["Fatal", "Attempted to get index of header %s, which does not exist." %header])
        return None

    @abstractmethod
    def default_config(self):
        pass

    @abstractmethod
    def spin_up(self):
        pass

    @abstractmethod
    def headers(self):
        pass

    @abstractmethod
    def next_row(self):
        pass

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def get_value(self, column, column_type):
        pass

    @abstractmethod
    def set_table(self, table_name):
        pass

    @abstractmethod
    def tables(self):
        pass
