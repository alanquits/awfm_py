from .theisdrawdownmodel import TheisDrawdownModel
from .hantushjacobdrawdownmodel import HantushJacobDrawdownModel

def AquiferDrawdownModel(model_name, params):
    if model_name == "theis":
        return TheisDrawdownModel(params["S"], params["T"])
    elif model_name == "hantush-jacob":
        return HantushJacobDrawdownModel(params["S"], params["T"], params["m*/K*"])
    else:
        return None
