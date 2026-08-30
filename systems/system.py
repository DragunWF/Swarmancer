from abc import ABC, abstractmethod

class System(ABC):
    @abstractmethod
    def update(self, entities, dt):
        pass
