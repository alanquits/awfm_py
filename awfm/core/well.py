from .timeseries import Timeseries
from .transientparameter import ConstantParameter, LinearParameter, param_units_common
from .units import to_std_units_factor, from_std_units_factor

import numpy as np

class Well:
    def __init__(self, name, x, y, rw=1.0):
        self.name = name
        self.x = x
        self.y = y
        self.rw = 1.0
        self.set_rw(rw)
        self.h0 = ConstantParameter(0, param_units_common["h"])
        self.b = ConstantParameter(0, param_units_common["B"])
        self.c = ConstantParameter(0, param_units_common["C"])
        self.h = Timeseries()
        self.Q = Timeseries()
        self.mod = {
            "ts": np.array([], dtype='float64'),
            "s_aq": np.array([], dtype='float64'),
            "s_w": np.array([], dtype='float64'),
            "h0": np.array([], dtype='float64'),
            "h": np.array([], dtype='float64')
        }

    def __str__(self):
        s = "Well: %s\n" %self.name
        s += "    location: %lf, %lf\n" %(self.x, self.y)
        s += "    rw      : %lf\n" %self.rw
        s += "    h0      : %s\n" %self.h0.to_sql_string()
        s += "    b       : %s\n" %self.b.to_sql_string()
        s += "    c       : %s\n" %self.c.to_sql_string()
        return s

    def distance_to_point(self, x, y):
        dx = self.x - x
        dy = self.y - y
        return max(np.sqrt(dx*dx + dy*dy), self.rw)

    def distance_to_well(self, w):
        return self.distance_to_point(w.x, w.y)

    def normalize_units(self, factor_generator, units):
        'factor_generator is either to_std_units_factor or from_std_units_factor'
        length_factor = factor_generator("length", units["length"])
        time_factor = factor_generator("time", units["time"])
        discharge_factor = factor_generator("discharge", units["discharge"])

        self.x *= length_factor
        self.y *= length_factor
        self.rw *= length_factor
        self.h.ts *= time_factor
        self.h.vs *= length_factor
        self.Q.ts *= time_factor
        self.Q.vs *= discharge_factor

        for key in self.mod.keys():
            if key == "ts":
                self.mod[key] *= time_factor
            else:
                self.mod[key] *= length_factor

    def set_rw(self, rw):
        if rw > 0:
            self.rw = rw

    def run_model(self, ts, pumping_wells, aquifer_drawdown_model):
        # print("running model at well %s" %self.name)
        self.mod["ts"] = ts
        self.mod["s_aq"] = self.model_aquifer_drawdown(ts, pumping_wells, aquifer_drawdown_model)
        self.mod["s_w"] = self.model_well_loss(ts)
        self.mod["h0"] = self.model_h0(ts)
        self.mod["t"] = self.mod["h0"] - (self.mod["s_aq"] + self.mod["s_w"])

    def model_aquifer_drawdown(self, ts, pumping_wells, aquifer_drawdown_model):
        # print("\n\nmodel_aquifer_drawdown at %s" %self.name)
        # input()
        vs = np.zeros([len(ts)])
        for pumping_well in pumping_wells:
            # print("   ... modeling pumping at %s" %pumping_well.name)
            vs += aquifer_drawdown_model.model_drawdown_from_well(ts, self.x, self.y, pumping_well)
        return vs

    def model_well_loss(self, ts):
        vs = []
        for i in range(0, len(ts)):
            Q = self.Q.value_at_t(ts[i])
            C = self.c.value_at_t(ts[i])
            B = self.b.value_at_t(ts[i])
            if Q is None:
                Q = 0
            s_w = Q*B + Q*C**2
            vs.append(s_w)
        return np.array(vs, dtype="float64")

    def model_h0(self, ts):
        vs = []
        for i in range(0, len(ts)):
            vs.append(self.h0.value_at_t(ts[i]))
        return np.array(vs, dtype="float64")
