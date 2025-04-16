#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: 3.10.8.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore
import osmosdr
import time
import sip
import threading



class energy_detection(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "energy_detection")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.px_clocks = px_clocks = [297000000, 297000000, 297000000, 297000000, 296703000, 296752500, 297000000, 297000000, 296703000, 296752500, 148500000, 148500000, 148351500, 74250000, 74250000, 74250000, 74175750, 74188125, 108000468, 108000000, 74250000, 74250000, 74175750, 64995840, 40002293, 27000000, 27027000, 26999973, 25200000, 25174800]
        self.mode = mode = 0
        self.px_rate = px_rate = px_clocks[mode]
        self.harmonic = harmonic = 1
        self.samp_rate = samp_rate = 10e6
        self.modes = modes = ['3840x2160@30.0', '4096x2160@30.0', '4096x2160@25.0', '4096x2160@24.0', '4096x2160@29.97', '4096x2160@23.98', '3840x2160@25.0', '3840x2160@24.0', '3840x2160@29.97', '3840x2160@23.98', '1920x1080@60.0', '1920x1080@50.0', '1920x1080@59.94', '1920x1080@30.0', '1920x1080@25.0', '1920x1080@24.0', '1920x1080@29.97', '1920x1080@23.98', '1280x1024@60.02', '1280x960@60.0', '1280x720@60.0', '1280x720@50.0', '1280x720@59.94', '1024x768@60.0', '800x600@60.32', '720x576@50.0', '720x480@60.0', '720x480@59.94', '640x480@60.0', '640x480@59.94']
        self.low_cut = low_cut = 20000
        self.high_cut = high_cut = 4e6
        self.freq = freq = px_rate*harmonic
        self.variable_function_probe_0 = variable_function_probe_0 = 0
        self.variable_qtgui_label_0 = variable_qtgui_label_0 = (variable_function_probe_0 + 30)

        ##################################################
        # Blocks
        ##################################################

        self.meting_level = blocks.probe_signal_f()
        self._low_cut_range = Range(1, samp_rate/2, 1, 20000, 200)
        self._low_cut_win = RangeWidget(self._low_cut_range, self.set_low_cut, "'low_cut'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._low_cut_win)
        self._high_cut_range = Range(1, samp_rate/2, 1, 4e6, 200)
        self._high_cut_win = RangeWidget(self._high_cut_range, self.set_high_cut, "'high_cut'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._high_cut_win)
        self.qtgui_sink_x_0 = qtgui.sink_c(
            1024, #fftsize
            window.WIN_BLACKMAN_hARRIS, #wintype
            freq, #fc
            samp_rate, #bw
            "", #name
            True, #plotfreq
            True, #plotwaterfall
            True, #plottime
            True, #plotconst
            None # parent
        )
        self.qtgui_sink_x_0.set_update_time(1.0/10)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_0.enable_rf_freq(False)

        self.top_layout.addWidget(self._qtgui_sink_x_0_win)
        self.osmosdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + ""
        )
        self.osmosdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(freq, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(10, 0)
        self.osmosdr_source_0.set_if_gain(20, 0)
        self.osmosdr_source_0.set_bb_gain(20, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(0, 0)

        self.band_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.band_pass(
                1,
                samp_rate,
                low_cut,
                high_cut,
                100000,
                window.WIN_HAMMING,
                6.76))
        
        ##########################################################
        ######################### ADDED ##########################
        ##########################################################
        # Create the options list
        self._mode_options = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
        # Create the labels list
        self._mode_labels = ['3840x2160@30.0', '4096x2160@30.0', '4096x2160@25.0', '4096x2160@24.0', '4096x2160@29.97', '4096x2160@23.98', '3840x2160@25.0', '3840x2160@24.0', '3840x2160@29.97', '3840x2160@23.98', '1920x1080@60.0', '1920x1080@50.0', '1920x1080@59.94', '1920x1080@30.0', '1920x1080@25.0', '1920x1080@24.0', '1920x1080@29.97', '1920x1080@23.98', '1280x1024@60.02', '1280x960@60.0', '1280x720@60.0', '1280x720@50.0', '1280x720@59.94', '1024x768@60.0', '800x600@60.32', '720x576@50.0', '720x480@60.0', '720x480@59.94', '640x480@60.0', '640x480@59.94']
        # Create the combo box
        self._mode_tool_bar = Qt.QToolBar(self)
        self._mode_tool_bar.addWidget(Qt.QLabel("Display's resolution" + ": "))
        self._mode_combo_box = Qt.QComboBox()
        self._mode_tool_bar.addWidget(self._mode_combo_box)
        for _label in self._mode_labels: self._mode_combo_box.addItem(_label)
        self._mode_callback = lambda i: Qt.QMetaObject.invokeMethod(self._mode_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._mode_options.index(i)))
        self._mode_callback(self.mode)
        self._mode_combo_box.currentIndexChanged.connect(
            lambda i: self.set_mode(self._mode_options[i]))
        
        # Create the radio buttons
        self.top_grid_layout.addWidget(self._mode_tool_bar, 2, 0, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)

        # Create harmonic slider
        self._harmonic_range = Range(1, 5, 1, 1, 200)
        self._harmonic_win = RangeWidget(self._harmonic_range, self.set_harmonic, "'harmonic'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._harmonic_win)

        # Computation of power
        self._variable_qtgui_label_0_tool_bar = Qt.QToolBar(self)
        if None:
            self._variable_qtgui_label_0_formatter = None
        else:
            # Here is set the value of power measurement
            self._variable_qtgui_label_0_formatter = lambda x: eng_notation.num_to_str(x)

        # Power measurement label display
        self._variable_qtgui_label_0_tool_bar.addWidget(Qt.QLabel("Power:"))
        # Power mesurement display
        self._variable_qtgui_label_0_label = Qt.QLabel(str(self._variable_qtgui_label_0_formatter(self.variable_qtgui_label_0)))
        self._variable_qtgui_label_0_tool_bar.addWidget(self._variable_qtgui_label_0_label)
        
        def _variable_function_probe_0_probe():
          while True:

            print(str(self._variable_qtgui_label_0_formatter(self.variable_qtgui_label_0)))
            val = self.meting_level.level()
            try:
              try:
                self.doc.add_next_tick_callback(functools.partial(self.set_variable_function_probe_0,val))
              except AttributeError:
                self.set_variable_function_probe_0(val)
            except AttributeError:
              pass
            time.sleep(1.0 / (2))

        _variable_function_probe_0_thread = threading.Thread(target=_variable_function_probe_0_probe)
        _variable_function_probe_0_thread.daemon = True
        _variable_function_probe_0_thread.start()



        self.blocks_nlog10_ff_0 = blocks.nlog10_ff(10, 1, 0)
        self.blocks_moving_average_xx_0 = blocks.moving_average_ff(50000, (20e-6), 4000, 1)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)


        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_moving_average_xx_0, 0))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.blocks_nlog10_ff_0, 0))
        self.connect((self.band_pass_filter_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.blocks_nlog10_ff_0, 0), (self.meting_level, 0))


        ##################################################
        # Connections
        ##################################################
        self.connect((self.band_pass_filter_0, 0), (self.qtgui_sink_x_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.band_pass_filter_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "energy_detection")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_px_clocks(self):
        return self.px_clocks

    def set_px_clocks(self, px_clocks):
        self.px_clocks = px_clocks
        self.set_px_rate(self.px_clocks[self.mode])

    def get_mode(self):
        return self.mode

    def set_mode(self, mode):
        self.mode = mode
        self._mode_callback(self.mode)
        self.set_px_rate(self.px_clocks[self.mode])

    def get_px_rate(self):
        return self.px_rate

    def set_px_rate(self, px_rate):
        self.px_rate = px_rate
        self.set_freq(self.px_rate*self.harmonic)

    def get_harmonic(self):
        return self.harmonic

    def set_harmonic(self, harmonic):
        self.harmonic = harmonic
        self.set_freq(self.px_rate*self.harmonic)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.band_pass_filter_0.set_taps(firdes.band_pass(1, self.samp_rate, self.low_cut, self.high_cut, 100000, window.WIN_HAMMING, 6.76))
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)
        self.qtgui_sink_x_0.set_frequency_range(self.freq, self.samp_rate)

    def get_modes(self):
        return self.modes

    def set_modes(self, modes):
        self.modes = modes

    def get_low_cut(self):
        return self.low_cut

    def set_low_cut(self, low_cut):
        self.low_cut = low_cut
        self.band_pass_filter_0.set_taps(firdes.band_pass(1, self.samp_rate, self.low_cut, self.high_cut, 100000, window.WIN_HAMMING, 6.76))

    def get_high_cut(self):
        return self.high_cut

    def set_high_cut(self, high_cut):
        self.high_cut = high_cut
        self.band_pass_filter_0.set_taps(firdes.band_pass(1, self.samp_rate, self.low_cut, self.high_cut, 100000, window.WIN_HAMMING, 6.76))

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_source_0.set_center_freq(self.freq, 0)
        self.qtgui_sink_x_0.set_frequency_range(self.freq, self.samp_rate)

    # Power measurement 
    def get_variable_function_probe_0(self):
        return self.variable_function_probe_0

    def set_variable_function_probe_0(self, variable_function_probe_0):
        self.variable_function_probe_0 = variable_function_probe_0
        self.set_variable_qtgui_label_0((self.variable_function_probe_0 + 30))

    def get_variable_qtgui_label_0(self):
        return self.variable_qtgui_label_0

    def set_variable_qtgui_label_0(self, variable_qtgui_label_0):
        self.variable_qtgui_label_0 = variable_qtgui_label_0
        Qt.QMetaObject.invokeMethod(self._variable_qtgui_label_0_label, "setText", Qt.Q_ARG("QString", str(self._variable_qtgui_label_0_formatter(self.variable_qtgui_label_0))))




def main(top_block_cls=energy_detection, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
