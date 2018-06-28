import os
import sys
awfm_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, awfm_root)

from awfm.core import Timeseries

def timeseries_zero_below_magnitude(outfile):
  ts = Timeseries()
  ts.append(0, 10)
  ts.append(1, 400)
  ts.append(2, 410)
  ts.append(3, 403)
  ts.append(4, 404)
  ts.append(5, 5)
  ts.append(6, 7)
  ts.append(7, 6)
  ts.append(8, 405)
  ts.append(9, 399)
  ts.append(10, 401)
  ts_mod = ts.zero_below_magnitude(50)

if __name__ == "__main__":
  timeseries_zero_below_magnitude("timeseries.zero_below_magnitude")