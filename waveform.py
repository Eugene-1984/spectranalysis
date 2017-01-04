# -*- coding: utf-8 -*-

import numpy as np
import scipy.io.wavfile

from numpy import arange, vstack
from numpy.fft import fft, fftfreq


WINDOW_LENGTH = 1024
STEP = 1024 * 2


class Waveform(object):

    def __init__(self, file_name, window_length=WINDOW_LENGTH, step=STEP):

        self.rate, iq = scipy.io.wavfile.read(file_name)
        self.a = iq[:, 0] - 1j * iq[:, 1]
        self.a /= np.linalg.norm(self.a)

        self.window_length = window_length
        self.step = step

        self.spectrogram = self._get_spectrogram()
        self.psd = self.get_psd()

    def get_psd(self):
        return self.spectrogram.mean(axis=0)

    @property
    def duration(self):
        return len(self) * 1. / self.rate

    @property
    def t(self):
        return arange(len(self) / self.step) * self.step * 1. / self.rate

    @property
    def f(self):
        return fftfreq(self.window_length, d=1. / self.rate)

    def __len__(self):
        return self.a.shape[0]

    @staticmethod
    def split(sequence, window_length, step):
        i = 0
        while True:
            l = i * step
            r = i * step + window_length

            if r > len(sequence):
                break
            else:
                yield sequence[l: r]
                i += 1

    def _get_spectrogram(self):
        slices_t = vstack([i for i in Waveform.split(self.a, self.window_length, self.step)])
        slices_f = fft(slices_t)
        return slices_f



