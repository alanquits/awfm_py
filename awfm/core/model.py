from .well import Well
from .aquiferdrawdownmodel import TheisDrawdownModel, HantushJacobDrawdownModel
from .units import from_std_units_factor, to_std_units_factor, UNITS

import numpy as np
from scipy.optimize import leastsq, least_squares

class Model:
    def __init__(self):
        self.wells = {}
        self.aquifer_drawdown_model = TheisDrawdownModel()
        self.units = {
            "length": "meters",
            "time": "days",
            "discharge": "m3/day"
        }
        self.errors = []
        self.pest_settings = {
            "L_min": 1e-6,
            "L_max": 1e6
        }

    def add_well(self, w):
        if w.name in self.wells.keys():
            self.errors = ["Warning", "Attempted to insert a well (%s) without a unique name" %w.name]
        self.wells[w.name] = w

    def normalize_units(self, factor_generator):
        for well_name in self.well_names():
            self.wells[well_name].normalize_units(factor_generator, self.units)
        self.aquifer_drawdown_model.normalize_units(factor_generator, self.units)

    def run_model(self):
        self.normalize_units(to_std_units_factor)
        pumping_wells = self.wells_as_list()
        for well_name in self.wells.keys():
            w = self.wells[well_name]
            self.wells[well_name].run_model(w.h.ts, pumping_wells, self.aquifer_drawdown_model)
        self.normalize_units(from_std_units_factor)

    def run_pest_aquifer_drawdown(self):
        def objective_function(params_arr):
            self.aquifer_drawdown_model.set_sorted_params_array(params_arr)
            residuals = np.array([], dtype="float64")
            pumping_wells = self.wells_as_list()
            for well_name in self.wells.keys():
                residuals_part = self.wells[well_name].run_pest_aquifer_drawdown_residuals(pumping_wells, self.aquifer_drawdown_model, self.pest_settings) 
                if len(residuals_part) > 0:
                    residuals = np.concatenate([residuals, residuals_part])
            return residuals

        self.normalize_units(to_std_units_factor)
        
        res = least_squares(objective_function, \
            self.aquifer_drawdown_model.get_sorted_params_array(), \
            method='lm')

        self.normalize_units(from_std_units_factor)

    def set_unit(self, unit_type, unit):
        if unit_type in UNITS.keys():
            if unit in UNITS[unit_type].keys():
                self.units[unit_type] = unit

    def set_units(self, d):
        for unit_type in d.keys():
            self.set_unit(unit_type, d[unit_type])

    def wells_as_list(self):
        ws = []
        for well_name in self.wells.keys():
            ws.append(self.wells[well_name])
        return ws

    def well_names(self):
        return list(sorted(self.wells.keys()))
