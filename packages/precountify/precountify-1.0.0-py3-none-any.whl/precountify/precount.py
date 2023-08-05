from .audio.audio_file import AudioFile
from .click import Click
from .margin import Margin


class Precount:
    def __init__(self, audio):
        assert isinstance(audio, AudioFile)
        self.audio = audio

    def prepend(self, margin):
        assert isinstance(margin, Margin)
        audio = margin.audio.append(self.audio)
        return Precount(audio)

    @classmethod
    def from_click(cls, click, meter, measure, upbeat):
        assert isinstance(click, Click)
        assert meter > 0
        assert measure > 0
        assert meter > upbeat >= 0

        n_beats = cls.n_beats(meter, measure, upbeat)
        audio = click.audio.tile(n_beats)
        return cls(audio)

    @classmethod
    def n_beats(cls, meter, measure, upbeat):
        return meter * measure - upbeat
