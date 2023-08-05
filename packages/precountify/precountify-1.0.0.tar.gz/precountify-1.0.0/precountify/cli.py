import fire

from .precountify import precountify


def run(
    input_file, output_file,
    sr=None, bpm=None, click=None,
    meter=4, measure=2, upbeat=0, offset=0, margin=0,
    estimator='precountify.estimator.librosa.LibrosaTempoEstimator'
):
    precountified = precountify(
        input_file,
        sr, bpm, click,
        meter, measure, upbeat, offset, margin,
        estimator)
    precountified.save(output_file)


def main():
    fire.Fire(run)


if __name__ == '__main__':
    main()
