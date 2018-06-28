import os
import sys
awfm_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, awfm_root)

from awfm.core import Timeseries
from definition import *
import matplotlib.pylab as plt
import matplotlib

font = {'size'   : 16}

matplotlib.rc('font', **font)

def timeseries_zero_below_magnitude(outfile):
  ts = Timeseries()
  ts.append(0, 10)
  ts.append(1, 100)
  ts.append(2, 110)
  ts.append(3, 104)
  ts.append(4, 5)
  ts.append(5, 7)
  ts.append(6, 6)
  ts.append(7, 105)
  ts.append(8, 99)
  ts.append(9, 101)

  mag_cutoff = 20
  ts_mod = ts.zero_below_magnitude(mag_cutoff)

  def gen_plot(ts, outfile):
    fig = plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))
    ax = fig.gca()

    ts_block, vs_block = to_block_pumping(ts.ts, ts.vs)
    ax.fill_between(ts_block, 0, vs_block)
    ax.plot([0, 10], [mag_cutoff]*2, 'r--')
    ax.set_xlabel("Time (days)")
    ax.set_ylabel("Pumping Rate (gpm)")

    ax.set_ylim([0, ax.get_ylim()[1]])

    plt.tight_layout()
    plt.savefig(outfile)
    plt.close(fig)

  gen_plot(ts, outfile + "_before.pdf")
  gen_plot(ts_mod, outfile + "_after.pdf")

if __name__ == "__main__":
  timeseries_zero_below_magnitude("timeseries_zero_below_magnitude")