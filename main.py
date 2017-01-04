#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QTabWidget, QFileDialog, QLabel)

from waveform import Waveform
from plots import (SpectrogramWidget, PowerSpectralDensityWidget)

PROGRAM_TITLE = 'SpectraAnalysis'


class TabWidget(QTabWidget):

    def __init__(self, parent):

        super().__init__(parent)

        self.spectrogram = SpectrogramWidget()
        self.psd = PowerSpectralDensityWidget()

        self.addTab(self.psd, "Power Spectral Density")
        self.addTab(self.spectrogram, "Spectrogram")


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.status_bar = self.statusBar()
        self.status_bar_label = QLabel()
        self.status_bar.addPermanentWidget(self.status_bar_label)

        # Exit
        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(QApplication.instance().quit)

        # Load Waveform
        lw_action = QAction('Load waveform', self)
        lw_action.setShortcut('Ctrl+O')
        lw_action.triggered.connect(self.load_waveform)

        # About
        about_action = QAction('&About', self)
        about_action.setShortcut('F1')
        about_action.triggered.connect(self.about)

        # Menu bar
        menu_bar = self.menuBar()

        # -- File
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(lw_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # -- Help
        help_menu = menu_bar.addMenu('&Help')
        help_menu.addAction(about_action)

        # Main window parameters
        self.setGeometry(300, 600, 600, 420)
        self.setWindowTitle(PROGRAM_TITLE)

        self.tab_widget = TabWidget(self)
        self.setCentralWidget(self.tab_widget)

        self.show()

        # DEBUG:
        self._open_waveform('/home/eugene/Development/playground/csexamples/waveforms/ERMES IQ.wav')

    def load_waveform(self):

        open_dialog = QFileDialog()
        open_dialog.setFileMode(QFileDialog.ExistingFile)
        open_dialog.setNameFilters(["Waveform file (*.wav)"])

        if open_dialog.exec_():
            file_names = open_dialog.selectedFiles()
            self._open_waveform(file_names[0])

    def _open_waveform(self, file_name):

        self.waveform = Waveform(file_name)

        # Display metrics
        message = 'Waveform: <b>%d</b> samples @ <b>%d</b> kHz' % (len(self.waveform), self.waveform.rate * 1e-3)
        self.status_bar_label.setText(message)

        # Update plots
        self.tab_widget.spectrogram.set_waveform(self.waveform)
        self.tab_widget.psd.set_waveform(self.waveform)

    def about(self):
        QtWidgets.QMessageBox.about(self, "About", """Copyright GPL - Eugene""")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
