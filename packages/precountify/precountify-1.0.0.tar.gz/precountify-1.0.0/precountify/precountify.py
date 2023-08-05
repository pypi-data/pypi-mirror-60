from .click import Click
from .margin import Margin
from .music import Music
from .precount import Precount
from .util import import_string


def precountify(
    input_file,
    sr=None, bpm=None, click=None,
    meter=4, measure=2, upbeat=0, offset=0, margin=0,
    estimator='precountify.estimator.librosa.LibrosaTempoEstimator',
):
    music = Music.from_file(input_file, sr).trimmed()

    if offset > 0:
        music = music.offsetted(offset)

    if bpm is None:
        estimator_cls = import_string(estimator)
        bpm = estimator_cls.estimate(music.audio)
        print('[INFO] estimated bpm:', bpm)

    if click is None:
        click = Click.preset()

    click = Click(click, music.audio.sr, bpm, music.audio.is_mono())
    precount = Precount.from_click(click, meter, measure, upbeat)

    if margin > 0:
        margin = Margin(margin, music.audio.sr, music.audio.is_mono())
        precount = precount.prepend(margin)

    precountified = music.prepend(precount).audio
    return precountified
