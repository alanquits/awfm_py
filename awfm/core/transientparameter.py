from abc import ABC, abstractmethod

class TransientParameter(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def value_at_t(self, t):
        pass

    @abstractmethod
    def to_sql_string(self):
        pass

    @abstractmethod
    def from_sql_string(self, s):
        pass

class ConstantParameter(TransientParameter):
    def __init__(self, value):
        self.value = value

    def value_at_t(self, t):
        return self.value

    def to_sql_string(self):
        return "constant %lf" %self.value

    def from_sql_string(self, s):
        _, v = s.split()
        self.value = float(v)

class LinearParameter(TransientParameter):
    def __init__(self, value_at_t0, dv_dt):
        self.value_at_t0 = value_at_t0
        self.dv_dt = dv_dt

    def value_at_t(self, t):
        return self.dv_dt*t + self.value_at_t0

    def to_sql_string(self):
        return "linear %lf %lf" %(self.value_at_t0, self.dv_dt)

    def from_sql_string(self, s):
        _, b, m = s.split()
        self.value_at_t0 = float(b)
        self.dv_dt = float(m)

def from_sql_string(s):
    values = s.split()
    if values[0].lower() == "constant":
        p = ConstantParameter(0)
        p.from_sql_string(s)
        return p
    elif values[0].lower() == "linear":
        p = LinearParameter(0, 0)
        p.from_sql_string(s)
        return p
    else:
        return None
