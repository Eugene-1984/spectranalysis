# -*- coding: utf-8 -*-

import matplotlib
import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from numpy import (flipud, abs)

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QSizePolicy, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSlider)

# From the matplotlib example:
# http://matplotlib.org/examples/user_interfaces/embedding_in_qt5.html
matplotlib.use('Qt5Agg')


class FigureCanvasWidget(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        self.figure = Figure(figsize=(width, height), dpi=dpi, facecolor='None', edgecolor='None')
        self.axes = self.figure.add_subplot(111, axisbg='black')

        self.axes.hold(False)

        FigureCanvas.__init__(self, self.figure)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class SliderFigureWidget(QWidget):

    def __init__(self):
        super(SliderFigureWidget, self).__init__()

        self.waveform = None

        # Slider
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setTickPosition(QSlider.TicksAbove)
        self.slider.valueChanged.connect(self.redraw)

        # matplotlib canvas
        self.figure_canvas = FigureCanvasWidget(self)

        # labeled slider
        hbox = QHBoxLayout()
        self.slider_label_min = QLabel()
        self.slider_label_max = QLabel()
        hbox.addWidget(self.slider_label_min)
        hbox.addWidget(self.slider)
        hbox.addWidget(self.slider_label_max)

        # vertical layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.figure_canvas)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def set_slider_options(self, waveform):

        bandwidth = waveform.rate * 1e-3
        value_min = bandwidth / 16.
        value_max = bandwidth
        self.slider.setMinimum(value_min)
        self.slider.setMaximum(value_max)
        self.slider.setTickInterval(bandwidth / 128.)

        self.slider_label_min.setText('%g kHz' % value_min)
        self.slider_label_max.setText('%g kHz' % value_max)

    @property
    def bandwidth(self):
        return self.slider.value()

    def set_waveform(self, waveform):
        self.waveform = waveform
        self.set_slider_options(waveform)

    def redraw(self):
        pass


class SpectrogramWidget(SliderFigureWidget):

    def _imshow(self, x, y, z, xmin, xmax, ymin, ymax):

        x_mask = (x >= xmin) & (x <= xmax)
        y_mask = (y >= ymin) & (y <= ymax)

        x = x[x_mask]
        y = y[y_mask]
        z = z[y_mask, :][:, x_mask]

        self.figure_canvas.axes.imshow(flipud(z), interpolation='nearest', aspect='auto',
                                       extent=(x[0], x[-1], y[0], y[-1]),
                                       cmap='jet', norm=matplotlib.colors.LogNorm())

    def redraw(self):

        spectrogram_f = self.waveform.spectrogram

        x = self.waveform.t
        y = np.fft.fftshift(self.waveform.f * 1e-3)
        z = np.fft.fftshift(np.abs(spectrogram_f), axes=1).T

        self._imshow(x, y, z, x[0], x[-1], -self.bandwidth / 2., self.bandwidth / 2.)

        self.figure_canvas.axes.set_xlabel(r'Time $t$, s')
        self.figure_canvas.axes.set_ylabel(r'Frequency $f$, kHz')
        self.figure_canvas.draw()


class PowerSpectralDensityWidget(FigureCanvasWidget):

    def set_waveform(self, waveform):

        x = np.fft.fftshift(waveform.f * 1e-3)
        y = np.fft.fftshift(abs(waveform.psd))

        self.axes.semilogy(x, y, 'y')

        self.axes.grid(b=True, which='major', color='grey')
        self.axes.grid(b=True, which='minor', color='grey')

        self.axes.set_xlabel(r'Frequency $f$, kHz')
        self.axes.set_ylabel(r'Magnitude, dB')
