import matplotlib.pylab as plt
import numpy as np

def float_compare(v1, v2, tol=1e-6):
    return abs(v1 - v2) < tol

class Timeseries:
    def __init__(self):
        self.ts = np.array([], dtype='f')
        self.vs = np.array([], dtype='f')
        self.errors = []

    def __eq__(self, other):
        if isinstance(other, Timeseries):
            if len(self.ts) == len(other.ts):
                for i in range(0, len(self.ts)):
                    if not float_compare(self.ts[i], other.ts[i]):
                        return False
                    if not float_compare(self.vs[i], other.vs[i]):
                        return False
        return True

    def __str__(self):
        s = "BEGIN Timeseries values\n"
        for i in range(0, len(self.ts)):
            s += "    %lf, %lf\n" %(self.ts[i], self.vs[i])
        s += "END Timeseries values"
        return s

    def _append(self, t, v):
        self.ts = np.append(self.ts, t)
        self.vs = np.append(self.vs, v)

    def append(self, t, v):
        if len(self.ts) == 0:
            self._append(t, v)
        else:
            if (t > self.ts[-1]):
                self._append(t, v)
            else:
                self.errors.append({
                    "level": "Warning",
                    "message": "Unable to append value end of array. Times must be in order."
                })

    def average_by_sign(self):
        ts_out = Timeseries()
        if len(self.ts) == 0:
            return ts_out

        fst, lst = self.split_by_sign()
        while True:
            t, v = fst.average()
            ts_out.append(t, v)
            fst, lst = lst.split_by_sign()
            if len(fst.ts) == 0:
                break

        return ts_out

    def dv_dt(self):
        ts_out = Timeseries()
        ts_out.ts = self.ts
        if len(self.ts) <= 1:
            ts_out.vs = self.vs
        else:
            ts_out.vs = np.insert(np.diff(self.vs), 0, self.vs[0])

        return ts_out

    def average(self):
        if len(self.ts) == 0:
            return None
        else:
            return [self.ts[0], np.mean(self.vs)]

    def bourdet_numerical_average(self, L_min, L_max):
        def find_neighbor_forward(i):
            for j in range(i+1, self.size()):
                dt = self.ts[j] - self.ts[i]
                if dt >= L_min:
                    if dt > L_max:
                        return None
                    else:
                        return j

        def find_neighbor_backward(i):
            for j in range(i-1, -1, -1):
                dt = self.ts[i] - self.ts[j]
                if dt >= L_min:
                    if dt > L_max:
                        return None
                    else:
                        return j

        ts_out = Timeseries()

        if self.size() < 3:
            return ts_out

        for i in range(1, self.size()-1):
            forward_index = find_neighbor_forward(i)
            backward_index = find_neighbor_backward(i)
            if forward_index and backward_index:
                dt1 = self.ts[i] - self.ts[backward_index]
                dt2 = self.ts[forward_index] - self.ts[i]
                dv1 = self.vs[i] - self.vs[backward_index]
                dv2 = self.vs[forward_index] - self.vs[i]
               
                num = (dv1/dt1)*dt2 + (dv2/dt2)*dt1
                ts_out.append(self.ts[i], num/(dt1+dt2))

        return ts_out

    def consolidate_adjacent_equal_values(self):
        if len(self.ts) == 0:
            return self

        t_out = Timeseries()
        t_out._append(self.ts[0], self.vs[0])
        for i in range(1, len(self.vs)):
            if self.vs[i] != self.vs[i-1]:
                t_out._append(self.ts[i], self.vs[i])

        return t_out

    def extract_by_range(self, t0, tf):
        ts_out = Timeseries()
        for i in range(0, self.size()):
            if t0 <= self.ts[i] and self.ts[i] < tf:
                ts_out.append(self.ts[i], self.vs[i])
            if self.ts[i] >= tf:
                break

        return ts_out

    def value_range(self):
        if self.size() == 0:
            return None
        else:
            return [np.min(self.vs), np.max(self.vs)]

    def round_to_nearest(self, v):
        if len(self.ts) == 0:
            return self

        ts_out = Timeseries()
        for i in range(0, len(self.ts)):
            rounded_value = round(self.vs[i]/v)*v
            ts_out._append(self.ts[i], rounded_value)

        return ts_out

    def plot(self, outfile=None, close_plot=True):
        fig = plt.figure(figsize=[11, 8.5])
        ax = fig.gca()
        ax.plot(self.ts, self.vs)
        if outfile:
            plt.savefig(outfile)
        else:
            plt.show()

        if close_plot:
            plt.close(fig)
            return None
        else:
            return [fig, ax]

    def sign(self, v):
        if v > 0:
            return 1
        elif v < 0:
            return -1
        else:
            return 0

    def size(self):
        return len(self.ts)

    def split_by_sign(self):
        def split_index():
            if len(self.ts) == 0:
                return None
            elif len(self.ts) == 1:
                return 1
            else:
                first_sign = self.sign(self.vs[0])
                for i in range(1, len(self.vs)):
                    if self.sign(self.vs[i]) != first_sign:
                        return i
                return len(self.vs)

        ts_out_fst = Timeseries()
        ts_out_lst = Timeseries()

        idx = split_index()
        if idx is None:
            return ts_out_fst, ts_out_lst

        ts_out_fst.ts = self.ts[0:idx]
        ts_out_fst.vs = self.vs[0:idx]

        ts_out_lst.ts = self.ts[idx:]
        ts_out_lst.vs = self.vs[idx:]

        return ts_out_fst, ts_out_lst

    def time_range(self):
        if self.size() == 0:
            return None
        else:
            return [np.min(self.ts), np.max(self.ts)]

    def value_at_t(self, t):
        if len(self.ts) == 0:
            return None
        else:
            if t < self.ts[0]:
                return None
            elif t >= self.ts[-1]:
                return self.vs[-1]
            else:
                for i in range(1, len(self.ts)):
                    if self.ts[i-1] <= t and t < self.ts[i]:
                        return self.vs[i]


    def zero_below_magnitude(self, magnitude):
        ts_out = Timeseries()
        for i in range(0, len(self.vs)):
            if abs(self.vs[i]) < abs(magnitude):
                ts_out._append(self.ts[i], 0)
            else:
                ts_out._append(self.ts[i], self.vs[i])

        return ts_out
