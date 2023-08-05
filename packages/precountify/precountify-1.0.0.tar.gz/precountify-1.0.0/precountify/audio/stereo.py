import numpy as np
import librosa

from .audio_file import AudioFile
from .mono import Mono


class Stereo(AudioFile):
    def __init__(self, data, sr, filename):
        assert data.ndim == 2 and data.shape[0] == 2
        super(Stereo, self).__init__(data, sr, filename)

    def resize(self, n):
        data = self.data.T.copy()
        data.resize(n, 2)
        return Stereo(data.T, self.sr, self.filename)

    def drop(self, n):
        return Stereo(self.data[:, n:], self.sr, self.filename)

    def append(self, that):
        assert self.data.ndim == that.data.ndim
        concat = np.concatenate([self.data, that.data], axis=1)
        return Stereo(concat, self.sr, self.filename)

    def tile(self, n):
        return Stereo(self._tile(n), self.sr, self.filename)

    def trim(self):
        return Stereo(self._trim(), self.sr, self.filename)

    def is_mono(self):
        return False

    def to_mono(self):
        return Mono(librosa.to_mono(self.data), self.sr, self.filename)

    @classmethod
    def empty(cls, sr, filename=None):
        data = np.empty((2, 0), dtype=np.float32)
        return cls(data, sr, filename)
