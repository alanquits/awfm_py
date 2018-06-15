from abc import ABC, abstractmethod

class AbstractDataframe(ABC):
    def __init__(self):
        super().__init__()
        self.errors = []

    def generate_column_lookup(self, named_record_map):
        for dst in named_record_map.keys():
            named_record_map[dst] = self.header_index(named_record_map[dst])

    @abstractmethod
    def config(self):
        pass

    @abstractmethod
    def spin_up(self):
        pass

    @abstractmethod
    def headers(self):
        pass

    @abstractmethod
    def header_index(self, hdr):
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
    def tables(self):
        pass
