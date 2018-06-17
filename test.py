from awfm.core.well import Well
from awfm.core.model import Model
from awfm.core import io, utils, Timeseries
from awfm.core.dataframe import Dataframe
from awfm.core.units import to_std_units_factor
from awfm.core.aquiferdrawdownmodel import TheisDrawdownModel

def float_compare(v1, v2, tol=1e-6):
    return abs(v1 - v2) < tol

def get_timeseries_from_file(path):
    ts = Timeseries()
    df = Dataframe(path)
    df.open()
    while df.next_row():
        t = df.get_value(0, float)
        v = df.get_value(1, float)
        ts.append(t, v)
    return ts

def run_test(name, method):
    passed = "PASSED" if method() else "FAILED"
    print("%s: %s" %(passed, name))

def test_fetter_pg_172():
    '''
    A well in a confined aquifer is pumped at a rate of 220 gal/min
    for 500 min. The aquifer is 48 ft thick. Time-drawdown data from
    an observation well located 824 ft away are given in Table 5.1
    (sample_data/fetter_pg172_drawdown_ft.dat). Find T, K, and S.

    Solution: S = 2.4e-5
              T = 1400 ft2/day
    '''

    model = Model()
    model.set_units({
        "length": "feet",
        "discharge": "gal/min"
    })

    model.add_well(Well("pumping well", 0, 0))
    model.add_well(Well("observation well", 824.0, 0))

    observed_drawdown = get_timeseries_from_file("sample_data/fetter_pg172_drawdown_ft.dat")
    observed_drawdown.ts *= to_std_units_factor("time", "minutes") # converts to days
    model.wells["observation well"].h = observed_drawdown

    Q = 220.0
    pumping_ts = Timeseries()
    pumping_ts.append(0, Q)
    model.wells["pumping well"].Q = pumping_ts

    model.aquifer_drawdown_model = TheisDrawdownModel(S=2.4e-5, T=1400)
    model.run_model()

    res = Timeseries()
    res.ts = model.wells["observation well"].mod["ts"]
    res.vs = model.wells["observation well"].mod["s_aq"]

    tol = 0.2
    for i in range(0, len(observed_drawdown.ts)):
        err = (observed_drawdown.vs[i] - res.vs[i]) / res.vs[i]
        if err > tol:
            return False

    return True

def test_well_distance_calcs():
    w1 = Well("w1", 0, 0, 1.0)
    w2 = Well("w2", 50, 0, 1.0)
    return float_compare(w1.distance_to_point(0, 30), 30) \
        and float_compare(w1.distance_to_well(w2), 50)

def initialize_and_save_model():
    m = Model()
    w = Well("w1", 0, 0)
    m.add_well(w)
    return io.save_model(m, "trash/model.db")

def open_and_resave_model():
    m = io.open_model("trash/model.db")
    if m is None:
        return False
    else:
        w = Well("w2", 0, 0)
        m.add_well(w)
        return io.save_model(m, "trash/model.db")

def test_read_wells_from_dataframe():
    infile = "sample_data/wells.csv"
    column_map = {
        "name": "well_id",
        "x": "x_coord",
        "y": "y_coord",
        "rw": "casing_radius",
        "h0": "initial_head"
    }
    table_name = None
    ws = utils.read_wells_from_dataframe(infile, column_map, table_name)
    if ws is None:
        return False
    else:
        return True

def timeseries_test(infile, method, args, outfile):
    ts_original = get_timeseries_from_file(infile)
    ts_modified = getattr(ts_original, method)(*args)
    ts_modified_check = get_timeseries_from_file(outfile)
    print(ts_modified)

    return ts_modified == ts_modified_check

def timeseries_test_series():
    if not timeseries_test("sample_data/ts1.dat", "zero_below_magnitude", \
                            [12,], "sample_data/ts1_zero_below_12.dat"):
        return False
    if not timeseries_test("sample_data/ts1.dat", "average_by_sign", \
                            [], "sample_data/ts1_average_by_sign.dat"):
        return False
    if not timeseries_test("sample_data/ts1.dat", "round_to_nearest", \
                            [10,], "sample_data/ts1_round_to_nearest_10.dat"):
        return False
    return True

if __name__ == "__main__":
    run_test("test_well_distance_calcs()", test_well_distance_calcs)
    run_test("initialize_and_save_model()", initialize_and_save_model)
    run_test("open_and_resave_model()", open_and_resave_model)
    run_test("test_read_wells_from_dataframe()", test_read_wells_from_dataframe)
    run_test("timeseries_test_series()", timeseries_test_series)
    run_test("test_fetter_pg_172()", test_fetter_pg_172)
