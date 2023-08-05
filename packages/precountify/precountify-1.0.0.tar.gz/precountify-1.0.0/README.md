# precountify
[![](https://github.com/akiomik/precountify/workflows/Python%20package/badge.svg)](https://github.com/akiomik/precountify/actions?query=workflow%3A%22Python+package%22)

A tool for adding pre-count (count-off) click to audio file.

## Requirements

- python >= 3.4

## Install

```sh
pip install precountify

# with madmom
pip install precountify[madmom]

# with essentia (linux only)
pip install precountify[essentia]
```

## Usage

```sh
# precountify INPUT_FILE OUTPUT_FILE
#   [--sr SAMPLE_RATE] [--bpm BPM] [--meter METER] [--measure N_MEASURES] [--upbeat N_UPBEATS]
#   [--offset OFFSET_IN_SECONDS] [--margin MARGIN_IN_SECONDS] [--click CLICK_FILE] [--estimator ESTIMATOR_MODULE]

# Add pre-count to output.wav with tempo estimation (using librosa)
precountify input.wav output.wav

# Add pre-count which has specified bpm
precountify input.wav output.wav --bpm 120

# Use `MadmomTempoEstimator`
precountify input.wav output.wav --estimator 'precountify.estimator.madmom.MadmomTempoEstimator'
```
