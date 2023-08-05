from madmom.features.beats import RNNBeatProcessor
from madmom.features.tempo import TempoEstimationProcessor

from .tempo_estimator import TempoEstimator


class MadmomTempoEstimator(TempoEstimator):
    @classmethod
    def estimate(cls, audio):
        proc = TempoEstimationProcessor(fps=100)
        act = RNNBeatProcessor()(audio.filename)
        [bpm, strength], *_ = proc(act)
        return bpm
