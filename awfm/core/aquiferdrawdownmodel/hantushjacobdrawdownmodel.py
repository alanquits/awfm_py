from .abstractaquiferdrawdownmodel import AbstractAquiferDrawdownModel

class HantushJacobDrawdownModel(AbstractAquiferDrawdownModel):
    def __init__(self, S=1e-3, T=100.0, m_over_K=1):
        self.S = S
        self.T = T
        self.m_over_K = m_over_K

    def name(self):
        return "hantush-jacob"
