import os
import sqlite3
from .db_schema import schema
from . import transientparameter as tp
from . import Well, Model
from .aquiferdrawdownmodel import TheisDrawdownModel, HantushJacobDrawdownModel

def delete_file_if_exists(infile):
    if os.path.exists(infile):
        os.remove(infile)

def create_empty_save_file(infile, return_connection=True):
    conn = sqlite3.connect(infile)
    curs = conn.cursor()
    for cmd in schema.split(";"):
        curs.execute(cmd)
    conn.commit()

    if return_connection:
        return conn, curs
    else:
        conn.close()
        return None, None

def render_value_to_sql(value):
    if isinstance(value, str):
        return "'%s'" %value
    elif value is None:
        return "NULL"
    elif isinstance(value, int):
        return "%d" %value
    elif isinstance(value, float):
        return "%lf" %value
    elif isinstance(value, bool):
        if value is True:
            return "TRUE"
        else:
            return "FALSE"
    else:
        print(str(value))
        assert(False)

def save_model(model, outfile):
    delete_file_if_exists(outfile)
    conn, curs = create_empty_save_file(outfile)

    def set_setting(setting_name, value):
        sql = "update settings set %s=%s" %(setting_name, render_value_to_sql(value))
        curs.execute(sql)

    for unit in ("length", "time", "discharge"):
        set_setting("%s_unit" %unit, model.units[unit])

    set_setting("aquifer_drawdown_model", model.aquifer_drawdown_model.name())

    for flag_name in model.flags.keys():
        set_setting(flag_name, model.flags[flag_name])

    for w in model.wells_as_list():
        sql = """
        insert into wells (name, x, y, rw, h0, b, c)
        values ('%s', %lf, %lf, %lf, '%s', '%s', '%s')
        """ %(w.name, w.x, w.y, w.rw, \
                w.h0.to_sql_string(), \
                w.b.to_sql_string(), \
                w.c.to_sql_string())
        curs.execute(sql)

    def set_aquifer_drawdown_parameter(name, value):
        sql = "update aquifer_drawdown_model_parameters set value=%lf where name='%s'" \
            %(value, name)
        curs.execute(sql)

    s_aq = model.aquifer_drawdown_model
    if s_aq.name() in ('theis', 'hantush-jacob'):
        set_aquifer_drawdown_parameter('S', s_aq.S)
        set_aquifer_drawdown_parameter('T', s_aq.T)

    if s_aq.name() == ('hantush-jacob'):
        set_aquifer_drawdown_parameter('m*/K*', s_aq.m_over_K)

    conn.commit()

    return True

def open_model(infile):
    conn = sqlite3.connect(infile)
    curs = conn.cursor()

    model = Model()

    # Read settings
    sql = """
    select length_unit
         , time_unit
         , discharge_unit
         , aquifer_drawdown_model
         , well_loss_turbulant_on
         , well_loss_laminar_on
    from settings
    """

    curs.execute(sql)
    record = curs.fetchone()
    if not record:
        conn.close()
        return False

    model.units["length"] = record[0]
    model.units["time"] = record[1]
    model.units["discharge"] = record[2]
    aquifer_drawdown_model_name = record[3] # complete later
    model.flags["well_loss_turbulant_on"] = record[4]
    model.flags["well_loss_laminar_on"] = record[5]

    # Read aquifer drawdown model parameters
    params = {}
    curs.execute("select name, value from aquifer_drawdown_model_parameters")
    for name, value in curs.fetchall():
        params[name] = value

    if aquifer_drawdown_model_name == "theis":
        model.aquifer_drawdown_model = \
            TheisDrawdownModel(S=params["S"], T=params["T"])
    elif aquifer_drawdown_model_name == "hantush-jacob":
        model.aquifer_drawdown_model = \
            HantushJacobDrawdownModel(S=params["S"], T=params["T"], m_over_K=params["m*/K*"])
    else:
        return False

    # Read wells
    sql = "select name, x, y, rw, h0, b, c from wells"
    curs.execute(sql)
    records = curs.fetchall()
    if records is not None:
        for name, x, y, rw, h0, b, c in records:
            h0 = tp.from_sql_string(h0)
            b = tp.from_sql_string(b)
            c = tp.from_sql_string(c)
            w = Well(name, x, y, rw)
            w.h0 = h0
            w.b = b
            w.c = c
            model.add_well(w)

    return model
