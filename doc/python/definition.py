import numpy as np

FIG_WIDTH = 6
FIG_HEIGHT = FIG_WIDTH*0.66

def to_block_pumping(ts, vs):
  ts_out = np.zeros([len(ts)*2])
  ts_out[0] = ts[0]
  ts_out[1:-1] = np.repeat(ts[1:], 2)
  ts_out[-1] = ts[-1] + (ts[-1] - ts[-2])*0.1

  vs_out = np.repeat(vs, 2)
  return ts_out, vs_out