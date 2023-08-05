import librosa

from .tempo_estimator import TempoEstimator


class LibrosaTempoEstimator(TempoEstimator):
    @classmethod
    def estimate(cls, audio):
        if not audio.is_mono():
            audio = audio.to_mono()

        onset_env = librosa.onset.onset_strength(audio.data, sr=audio.sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=audio.sr)
        return tempo[0]
