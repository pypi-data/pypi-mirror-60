import librosa

from .audio.mono import Mono
from .audio.stereo import Stereo


class Margin:
    def __init__(self, margin_in_seconds, sr, mono=False):
        assert margin_in_seconds >= 0
        assert sr > 0

        if mono:
            audio = Mono.empty(sr)
        else:
            audio = Stereo.empty(sr)

        self.margin_in_seconds = margin_in_seconds
        self.sr = sr
        self.audio = audio.resize(self.n_margin_samples())

    def n_margin_samples(self):
        return librosa.time_to_samples(self.margin_in_seconds, self.sr)
