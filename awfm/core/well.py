from .timeseries import Timeseries
from .transientparameter import ConstantParameter, LinearParameter, param_units_common
from .units import to_std_units_factor, from_std_units_factor
import numpy as np
import matplotlib.pylab as plt

def float_compare(v1, v2, tol=1e-3):
    return abs(v1 - v2) < tol

class Well:
    def __init__(self, name, x, y, rw=1.0):
        self.errors = []
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
        self.pest_windows = []

    def __str__(self):
        s = "Well: %s\n" %self.name
        s += "    location: %lf, %lf\n" %(self.x, self.y)
        s += "    rw      : %lf\n" %self.rw
        s += "    h0      : %s\n" %self.h0.to_sql_string()
        s += "    b       : %s\n" %self.b.to_sql_string()
        s += "    c       : %s\n" %self.c.to_sql_string()
        return s

    def append_pest_window(self, t0, tf):
        if self.is_valid_pest_window(t0, tf):
            self.pest_windows.append([float(t0), float(tf)])
        else:
            self.errors.append({
                    "level": "Warning",
                    "message": "Invalid pest window from %lf to %lf" %(t0, tf)
                })

    def distance_to_point(self, x, y):
        dx = self.x - x
        dy = self.y - y
        return max(np.sqrt(dx*dx + dy*dy), self.rw)

    def distance_to_well(self, w):
        return self.distance_to_point(w.x, w.y)

    def is_valid_pest_window(self, t0, tf):
        # Check if pumping is already occurring on at t0
        initial_pumping = self.Q.value_at_t(t0)
        
        if initial_pumping is None: # timeseries is empty or t0 is before start of timeseries
            pass
        elif initial_pumping > 0:
            return False
        else:
            pass

        # Check if any pumping begins between t0 and tf
        for i in range(0, self.Q.size()):
            if t0 <= self.Q.ts[i] and self.Q.ts[i] < tf:
                if self.Q.vs[i] > 0:
                    return False

        return True

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

        for i in range(0, len(self.pest_windows)):
            t0, tf = self.pest_windows[i]
            self.pest_windows[i] = [t0*time_factor, tf*time_factor]

    def set_rw(self, rw):
        if rw > 0:
            self.rw = rw

    def run_model(self, ts, pumping_wells, aquifer_drawdown_model):
        self.mod["ts"] = ts
        self.mod["s_aq"] = self.model_aquifer_drawdown(ts, pumping_wells, aquifer_drawdown_model)
        self.mod["s_w"] = self.model_well_loss(ts)
        self.mod["h0"] = self.model_h0(ts)
        self.mod["vs"] = self.mod["h0"] - (self.mod["s_aq"] + self.mod["s_w"])

    def run_pest_aquifer_drawdown_residuals(self, pumping_wells, aquifer_drawdown_model, pest_settings):
        L_min = pest_settings["L_min"]
        L_max = pest_settings["L_max"]
        residuals = np.array([], dtype="float64")
        for pest_window in self.pest_windows:
            t0, tf = pest_window
            obs_h = self.h.extract_by_range(t0, tf)
            
            mod_s_aq = Timeseries()
            mod_s_aq.ts = obs_h.ts     
            mod_s_aq.vs = self.model_aquifer_drawdown(obs_h.ts, pumping_wells, aquifer_drawdown_model)

            obs_h_avg = obs_h.bourdet_numerical_average(L_min, L_max)
            mod_s_aq_avg = mod_s_aq.bourdet_numerical_average(L_min, L_max)

            residuals_local = obs_h_avg.vs + mod_s_aq_avg.vs
            residuals = np.concatenate([residuals, residuals_local])

        return residuals

    def model_aquifer_drawdown(self, ts, pumping_wells, aquifer_drawdown_model):
        vs = np.zeros([len(ts)])
        for pumping_well in pumping_wells:
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
