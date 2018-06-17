from .abstractaquiferdrawdownmodel import AbstractAquiferDrawdownModel
import numpy as np
from scipy.special import expn

def W(u):
    return expn(1, u)

class TheisDrawdownModel(AbstractAquiferDrawdownModel):
    def __init__(self, S=1e-3, T=100.0):
        self.params = {
            "S": S,
            "T": T
        }

    def name(self):
        return "theis"

    def model_drawdown_from_well(self, ts, x, y, pumping_well):
        rw = pumping_well.distance_to_point(x, y)
        dQ = pumping_well.Q.dv_dt()
        vs = []
        S = self.params["S"]
        T = self.params["T"]
        for i in range(0, len(ts)):
            s_aq = 0
            t = ts[i]
            for j in range(0, len(dQ.ts)):
                if dQ.ts[j] < t:
                    dt = t - dQ.ts[j]
                    u = (rw**2*S) / (4*T*dt)
                    s_aq += (dQ.vs[j] / (4*np.pi*T)) * W(u)
                else:
                    break
            vs.append(s_aq)

        return np.array(vs)

    def normalize_units(self, factor_generator, units):
        length_factor = factor_generator("length", units["length"])
        time_factor = factor_generator("time", units["time"])
        self.params["T"] *= (length_factor**2) / time_factor
