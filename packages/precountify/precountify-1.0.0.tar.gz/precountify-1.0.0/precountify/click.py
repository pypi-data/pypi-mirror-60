import os

import librosa

from .audio.mono import Mono
from .audio.stereo import Stereo


class Click:
    def __init__(self, filename, sr, bpm, mono=False):
        assert sr > 0
        assert bpm > 0

        self.sr = sr
        self.bpm = bpm

        y, _ = librosa.load(filename, sr, mono=mono)
        if y.ndim == 1:
            audio = Mono(y, sr, filename)
        elif y.ndim == 2:
            audio = Stereo(y, sr, filename)
        else:
            raise ValueError('Click is supported only mono or stereo file.')
        self.audio = audio.resize(self.samples_per_beat())

    def seconds_per_beat(self):
        return 1 / (self.bpm / 60)

    def samples_per_beat(self):
        return librosa.time_to_samples(self.seconds_per_beat(), self.sr)

    @classmethod
    def preset(cls):
        return os.path.join(os.path.dirname(__file__), 'data/click.wav')
