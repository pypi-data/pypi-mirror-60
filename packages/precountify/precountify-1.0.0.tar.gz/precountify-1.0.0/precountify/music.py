import librosa

from .audio.audio_file import AudioFile
from .audio.mono import Mono
from .audio.stereo import Stereo
from .precount import Precount


class Music:
    def __init__(self, audio):
        assert isinstance(audio, AudioFile)
        self.audio = audio

    @classmethod
    def from_file(cls, filename, sr=None):
        assert sr is None or sr > 0

        y, sr = librosa.load(filename, sr, mono=False)
        if y.ndim == 1:
            audio = Mono(y, sr, filename)
        elif y.ndim == 2:
            audio = Stereo(y, sr, filename)
        else:
            raise ValueError('Music is supported only mono or stereo file.')

        return cls(audio)

    def trimmed(self):
        return Music(self.audio.trim())

    def offsetted(self, offset_in_seconds):
        assert offset_in_seconds >= 0
        n_offset_samples = librosa.time_to_samples(
                offset_in_seconds, self.audio.sr)
        return Music(self.audio.drop(n_offset_samples))

    def prepend(self, precount):
        assert isinstance(precount, Precount)
        audio = precount.audio.append(self.audio)
        return Music(audio)
