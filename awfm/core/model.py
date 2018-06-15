from .well import Well
from .aquiferdrawdownmodel import TheisDrawdownModel, HantushJacobDrawdownModel

class Model:
    def __init__(self):
        self.wells = {}
        self.aquifer_drawdown_model = TheisDrawdownModel()
        self.flags = {
            "well_loss_turbulant_on": False,
            "well_loss_laminar_on": False,
            "well_loss_transient_on": False,
            "h0_transient_on": False
        }
        self.units = {
            "length": "meters",
            "time": "days",
            "discharge": "m3/day"
        }
        self.errors = []

    def add_well(self, w):
        if w.name in self.wells.keys():
            self.errors = ["Warning", "Attempted to insert a well (%s) without a unique name" %w.name]
        self.wells[w.name] = w

    def wells_as_list(self):
        ws = []
        for well_name in self.wells.keys():
            ws.append(self.wells[well_name])
        return ws
