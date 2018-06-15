from awfm.core.well import Well
from awfm.core.model import Model
from awfm.core import io

def float_compare(v1, v2, tol=1e-6):
    return abs(v1 - v2) < tol

def run_test(name, method):
    passed = "PASSED" if method() else "FAILED"
    print("%s: %s" %(passed, name))

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
        print(m.wells.keys())
        return io.save_model(m, "trash/model.db")

if __name__ == "__main__":
    run_test("test_well_distance_calcs()", test_well_distance_calcs)
    run_test("initialize_and_save_model()", initialize_and_save_model)
    run_test("open_and_resave_model()", open_and_resave_model)
