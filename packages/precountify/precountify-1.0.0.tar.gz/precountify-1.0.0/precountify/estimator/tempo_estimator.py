from abc import ABC, abstractmethod


class TempoEstimator(ABC):
    @classmethod
    @abstractmethod
    def estimate(cls, audio):
        pass
