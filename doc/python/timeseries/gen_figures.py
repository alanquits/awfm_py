import os
import sys
awfm_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
print(awfm_root)
print("here-a")
import awfm

# from awfm.core import Timeseries
print("here-b")

def timeseries_zero_below_magnitude(outfile):
  ts = Timeseries()
  ts.append(0, 10)
  ts.append(1, 400)
  ts.append(2, 410)
  ts.append(3, 403)
  ts.append(4, 404)
  ts.append(5, 5)

  print(ts)