from abc import ABC, abstractmethod
from awfm.core.mixins import ParameterDict

param_units_common = {
    "B": (["time"], ["length"]*2),
    "C": (["time"]*2, ["length"]*5),
    "h": (["length"], [])
}

class TransientParameter(ABC, ParameterDict):
    def __init__(self):
        super().__init__()
        self.param_units = None

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
    def __init__(self, value, param_units):
        '''
        param units is length 2 tuple. The first item is a list of units
        in numerator and the second item is a list of units in denominator.
        For example, ft3/day is expressed as (["ft"]*3, ["day"])
        '''
        self.params = {
            "value": value
        }

        self.param_setters = {}
        self.param_units = param_units

    def normalize_units(self, factor_generator, units):
        factors = {
            "length": factor_generator("length", units["length"]),
            "time": factor_generator("time", units["time"]),
            "discharge": factor_generator("discharge", units["discharge"])
        }

        num, den = self.param_units
        for unit in num:
            self.params["value"] *= factors[unit]
        for unit in den:
            self.params["value"] /= factors[unit]


    def value_at_t(self, t):
        return self.params["value"]

    def to_sql_string(self):
        return "constant %lf" %self.params["value"]

    def from_sql_string(self, s):
        _, v = s.split()
        self.params["value"] = float(v)

class LinearParameter(TransientParameter):
    def __init__(self, value_at_t0, dv_dt, param_units):
        '''
        param units is length 2 tuple. The first item is a list of units
        in numerator and the second item is a list of units in denominator.
        For example, ft3/day is expressed as (["ft"]*3, ["day"])
        '''
        self.params = {
            "value_at_t0": value_at_t0,
            "dv_dt": dv_dt
        }

        self.param_setters = {}
        self.param_units = param_units

    def normalize_units(self, factor_generator, units):
        factors = {
            "length": factor_generator("length", units["length"]),
            "time": factor_generator("time", units["time"]),
            "discharge": factor_generator("discharge", units["discharge"])
        }

        num, den = self.param_units
        multiplier = 1
        for unit in num:
            multiplier *= factors[unit]
        for unit in den:
            multiplier /= factors[unit]

        self.params["value_at_t0"] *= multiplier
        self.params["dv_dt"] *= (multiplier / factors["time"])

    def value_at_t(self, t):
        return self.params["dv_dt"]*t + self.params["value_at_t0"]

    def to_sql_string(self):
        return "linear %lf %lf" %(self.params["value_at_t0"], self.params["dv_dt"])

    def from_sql_string(self, s):
        _, b, m = s.split()
        self.params["value_at_t0"] = float(b)
        self.params["dv_dt"] = float(m)

def from_sql_string(s):
    try:
        float(s)
        p = ConstantParameter(float(s))
        return p
    except:
        pass

    if not isinstance(s, str):
        return None

    values = s.split()
    if values[0].lower() == "constant":
        p = ConstantParameter(0, ([], []))
        p.from_sql_string(s)
        return p
    elif values[0].lower() == "linear":
        p = LinearParameter(0, 0, ([], []))
        p.from_sql_string(s)
        return p
    else:
        return None
