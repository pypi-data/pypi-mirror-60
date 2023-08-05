import numpy as np

from .audio_file import AudioFile


class Mono(AudioFile):
    def __init__(self, data, sr, filename):
        assert data.ndim == 1
        super(Mono, self).__init__(data, sr, filename)

    def resize(self, n):
        data = self.data.copy()
        data.resize(n)
        return Mono(data, self.sr, self.filename)

    def drop(self, n):
        return Mono(self.data[n:], self.sr, self.filename)

    def append(self, that):
        assert self.data.ndim == that.data.ndim
        concat = np.concatenate([self.data, that.data])
        return Mono(concat, self.sr, self.filename)

    def tile(self, n):
        return Mono(self._tile(n), self.sr, self.filename)

    def trim(self):
        return Mono(self._trim(), self.sr, self.filename)

    def is_mono(self):
        return True

    @classmethod
    def empty(cls, sr, filename=None):
        data = np.empty(0, dtype=np.float32)
        return cls(data, sr, filename)
