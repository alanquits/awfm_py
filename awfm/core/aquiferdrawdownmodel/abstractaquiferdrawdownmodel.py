from abc import ABC, abstractmethod

class AbstractAquiferDrawdownModel(ABC):
    @abstractmethod
    def name(self):
        pass
