from abc import ABC, abstractmethod
import numpy as np

class AbstractAquiferDrawdownModel(ABC):

    def __init__(self):
        self.params = {}
        self.param_setters = {}

    def get_sorted_params_array(self):
        arr = np.array([], dtype="float64")
        for key in list(sorted(self.params.keys())):
            arr = np.append(arr, self.params[key])
        return arr

    def set_sorted_params_array(self, arr):
        for i, param_name in enumerate(self.sorted_param_names()):
            self.set(param_name, arr[i])

    def set(self, param_name, value):
        if param_name in self.param_setters.keys():
            try:
                method_name = self.param_setters[param_name]
                getattr(self, method_name)(value)
            except:
                print("method name %s is not defined" %method_name)
                self.params[param_name] = value
        else:
            self.params[param_name] = value

    def sorted_param_names(self):
        return list(sorted(self.params.keys()))


    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def model_drawdown_from_well(self, ts, x, y, pumping_well):
        pass

    @abstractmethod
    def normalize_units(self, factor_generator, units):
        pass

    def __str__(self):
        s = "BEGIN AquiferDrawdownModel\n"
        s += "  name: %s\n" %self.name()
        for param_name in self.params.keys():
            s += "%s: %s\n" %(param_name, str(self.params[param_name]))
        s += "END AquiferDrawdownModel"
        return s
