
from abc import ABC, abstractmethod

class BaseCalculator(ABC):
    @abstractmethod
    def calculate(self):
        pass

    @abstractmethod
    def update(self, *args, **kwargs):
        pass
