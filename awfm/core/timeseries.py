class Timeseries:
    def __init__(self):
        self.ts = np.array(dtype='f')
        self.vs = np.array(dtype='f')
        self.errors = []

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

    def consolidate_adjacent_equal_values(self):
        if len(self.ts) == 0:
            return self

        t_out = Timeseries()
        t_out._append(self.ts[0], self.vs[0])
        for i in range(1, len(self.vs)):
            if self.vs[i] != self.vs[i-1]:
                t_out._append(self.ts[i], self.vs[i])

        return t_out

    def zero_below_magnitude(self, magnitude):
        t_out = Timeseries()
        for i in range(0, len(vs_out)):
            if abs(vs_out[i]) < abs(magnitude):
                ts_out._append(self.ts[i], 0)
            else:
                ts_out._append(self.ts[i], self.vs[i])

        return ts_out
