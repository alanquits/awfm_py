from .dataframe import Dataframe
import os
from .well import Well
from . import transientparameter as tp

def read_wells_from_dataframe(infile, column_map, table_name):
    # Verify that column_map has all required destinations
    required_destinations = ["name", "x", "y"]
    optional_destinations = ["rw", "h0", "b", "c"]

    user_destinations = column_map.keys()

    if len(set(required_destinations).intersection(set(user_destinations))) != len(required_destinations):
        print("read_wells_from_dataframe requires three destinations: [%s]" %",".join(required_destinations))
        return None

    # Try to open dataframe
    df = Dataframe(infile)
    if df is None:
        print("Dataframe() cannot infer file type from extension of %s" %infile)
        return None

    df.open()
    df.set_table(table_name)
    df.spin_up()

    index_of = df.generate_column_lookup(column_map)
    if df.errors:
        for err in df.errors:
            print(err)
        return None

    def get_mapped_value(v, column_type):
        if v in index_of.keys():
            if index_of[v] is None:
                return None
            else:
                return df.get_value(index_of[v], column_type)
        else:
            return None

    wells = []
    while df.next_row():
        name = df.get_value(index_of["name"], str)
        x = df.get_value(index_of["x"], float)
        y = df.get_value(index_of["y"], float)

        rw = get_mapped_value("rw", float)
        h0 = tp.from_sql_string(get_mapped_value("h0", str))
        b = tp.from_sql_string(get_mapped_value("b", str))
        c = tp.from_sql_string(get_mapped_value("c", str))

        w = Well(name, x, y)
        if rw is not None:
            w.set_rw(rw)

        if h0 is not None:
            w.h0 = h0

        if b is not None:
            w.b = b

        if c is not None:
            w.c = c

        wells.append(w)

    return wells
