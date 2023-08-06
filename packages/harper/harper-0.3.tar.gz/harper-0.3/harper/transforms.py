"""Transformation and wavelet functions."""
import math

import numpy as np


def generate_sine_sample(
    sample_index: int,
    frequency: float,
    amplitude: int = 16000,
    sampling_rate: int = 44100,
) -> int:
    """Generate a time series value from frequency domain attributes.

    Parameters
    ----------
    sample_index: int
        The index of the sample to be generated, related to its place
        in a series. Imagine starting at t0, this is x=0, which places
        our unit circle at (1,0) and has a corresponding sine value
        of 0. At 2, we will be at 2pi radians and back again at 0. This
        combines with the sampling_rate and frequency however.
    frequency: float
        The frequency of the wave we'd like to generate samples for. Hz.
    amplitude: int
        The magnitude by which we'd like to increase our generated samples.
        Defaults to 16000, ensuring samples fall between -32000 and 32000,
        a two-byte range.
    sampling_rate: int
        How frequently we'd like to sample from our wave. Defaults to 44100,
        a traditional value for CD-quality sound.

    """
    return int(
        amplitude
        * (math.sin(2 * math.pi * frequency * (sample_index / sampling_rate)))
    )


def generate_timeseries(spectrum):
    """Create timeseries data from a spectrum.

    Parameters
    ----------
    spectrum: list
        A simple spectrum to generate timeseries samples from.

    Returns
    -------
    List[int]
        A series of timeseries samples

    """
    timeseries = np.fft.ifft(spectrum)
    return list(complex_to_rounded_real(timeseries))


def complex_to_rounded_real(np_array):
    """Convert a complex array to a integer real number array.

    Parameters
    ----------
    np_array : numpy.ndarray
        A numpy array of complex numbers.

    Returns
    -------
    numpy.ndarray
        The real components of the array, rounded to integers.
    """
    return np.round(np.real(np_array)).astype("int")
    # return np.round(np.abs(np_array)).astype("int")


def complex_to_absolute_real_int(np_array):
    """Convert a complex array to an absolute integer real number array.

    Parameters
    ----------
    np_array : numpy.ndarray
        A numpy array of complex numbers.

    Returns
    -------
    numpy.ndarray
        The real components of the array, absolute and rounded to integers.
    """
    return np.round(np.abs(np_array)).astype("int")
