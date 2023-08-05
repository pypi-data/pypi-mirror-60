from essentia.standard import MonoLoader, StereoLoader, RhythmExtractor2013

from .tempo_estimator import TempoEstimator


class EssentiaTempoEstimator(TempoEstimator):
    @classmethod
    def estimate(cls, audio):
        if audio.is_mono():
            signal = MonoLoader(filename=audio.filename)()
        else:
            signal = StereoLoader(filename=audio.filename)()

        extractor = RhythmExtractor2013(method="multifeature")
        bpm, *_ = extractor(signal)
        return bpm
