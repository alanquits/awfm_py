from .abstractaquiferdrawdownmodel import AbstractAquiferDrawdownModel

class TheisDrawdownModel(AbstractAquiferDrawdownModel):
    def __init__(self, S=1e-3, T=100.0):
        self.S = S
        self.T = T

    def name(self):
        return "theis"
