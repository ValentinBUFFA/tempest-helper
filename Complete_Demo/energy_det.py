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
from gnuradio import uhd
from helpers import bcolors
from helpers import parse_mode_and_clock

# * GLOBAL VARIABLES for communication between classes
candidate_modes = []
candidate_freqs = []

HARMONIC_THRESHOLD = 500_000_000

class energy_detection(gr.top_block, Qt.QWidget):
    def __init__(self, verbose=False, sdr="hackrf", path_to_src="modes.txt"):
        self.verbose = verbose

        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme("gnuradio-grc"))
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

        self.px_clocks, self.modes = parse_mode_and_clock(path_to_src)
        # print(self.modes)
        # print(self.px_clocks)
        # print(len(self.modes))

        self.mode = mode = 0
        self.px_rate = self.px_clocks[mode]
        self.harmonic = 1
        self.samp_rate = 10e6
        self.low_cut = 20000
        self.high_cut = 1_000_000
        self.freq = self.px_rate * self.harmonic
        self.variable_function_probe_0 = 0
        self.variable_qtgui_label_0 = self.variable_function_probe_0 + 30
        self.ctr = 0
        self.px_idx = 0
        self.mean_clocks = []
        self.mean = 0
        self.tot_nb_freq = len(self.px_clocks)

        ##################################################
        # Blocks
        ##################################################

        self.meting_level = blocks.probe_signal_f()

        if sdr == "hackrf":
            self.osmosdr_source_0 = osmosdr.source(
                args="numchan=" + str(1) + " " + "hackrf=0"
            )
            self.osmosdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
            self.osmosdr_source_0.set_sample_rate(self.samp_rate)
            self.osmosdr_source_0.set_center_freq(self.freq, 0)
            self.osmosdr_source_0.set_freq_corr(0, 0)
            self.osmosdr_source_0.set_dc_offset_mode(0, 0)
            self.osmosdr_source_0.set_iq_balance_mode(0, 0)
            self.osmosdr_source_0.set_gain_mode(False, 0)
            self.osmosdr_source_0.set_gain(10, 0)
            self.osmosdr_source_0.set_if_gain(20, 0)
            self.osmosdr_source_0.set_bb_gain(20, 0)
            self.osmosdr_source_0.set_antenna("", 0)
            self.osmosdr_source_0.set_bandwidth(0, 0)
        elif sdr == "usrp":
            self.osmosdr_source_0 = uhd.usrp_source(
                ",".join(("addr=148.60.6.48", "")),
                uhd.stream_args(
                    cpu_format="fc32",
                    args="",
                    channels=list(range(0, 1)),
                ),
            )
            self.osmosdr_source_0.set_samp_rate(self.samp_rate)
            self.osmosdr_source_0.set_center_freq(self.freq, 0)
            self.osmosdr_source_0.set_antenna("RX2", 0)
            self.osmosdr_source_0.set_gain(0, 0)

        self.band_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.band_pass(
                1,
                self.samp_rate,
                self.low_cut,
                self.high_cut,
                100000,
                window.WIN_HAMMING,
                6.76,
            ),
        )

        ##################################################
        # Added
        ##################################################
        # Create the options list
        self._mode_options = range(0, len(self.px_clocks))

        # Create the combo box
        self._mode_tool_bar = Qt.QToolBar(self)
        self._mode_tool_bar.addWidget(Qt.QLabel("Display's resolution" + ": "))
        self._mode_combo_box = Qt.QComboBox()
        self._mode_tool_bar.addWidget(self._mode_combo_box)
        for _label in self.modes:
            self._mode_combo_box.addItem(_label)
        self._mode_callback = lambda i: Qt.QMetaObject.invokeMethod(
            self._mode_combo_box,
            "setCurrentIndex",
            Qt.Q_ARG("int", self._mode_options.index(i)),
        )
        self._mode_callback(self.mode)
        self._mode_combo_box.currentIndexChanged.connect(
            lambda i: self.set_mode(self._mode_options[i])
        )

        # Create the radio buttons
        self.top_grid_layout.addWidget(self._mode_tool_bar, 2, 0, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)

        # Computation of power
        self._variable_qtgui_label_0_tool_bar = Qt.QToolBar(self)
        if None:
            self._variable_qtgui_label_0_formatter = None
        else:
            # Here is set the value of power measurement
            self._variable_qtgui_label_0_formatter = lambda x: eng_notation.num_to_str(
                x
            )

        # Power measurement label display
        self._variable_qtgui_label_0_tool_bar.addWidget(Qt.QLabel("Pwr:"))
        # Power mesurement display
        self._variable_qtgui_label_0_label = Qt.QLabel(
            str(self._variable_qtgui_label_0_formatter(self.variable_qtgui_label_0))
        )
        self._variable_qtgui_label_0_tool_bar.addWidget(
            self._variable_qtgui_label_0_label
        )

        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            4096,  # size
            window.WIN_BLACKMAN_hARRIS,  # wintype
            self.freq,  # fc
            self.samp_rate,  # bw
            "",  # name
            1,
            None,  # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_0.set_y_label("Relative Gain", "dB")
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)

        labels = ["", "", "", "", "", "", "", "", "", ""]
        widths = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        colors = [
            "blue",
            "red",
            "green",
            "black",
            "cyan",
            "magenta",
            "yellow",
            "dark red",
            "dark green",
            "dark blue",
        ]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(
            self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget
        )
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_win)

        self.blocks_nlog10_ff_0 = blocks.nlog10_ff(10, 1, 0)
        self.blocks_moving_average_xx_0 = blocks.moving_average_ff(
            50000, (20e-6), 4000, 1
        )
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)

        self.blocks_correctiq_0 = blocks.correctiq()

        ##################################################
        # Thread of computation
        ##################################################

        def compute_level():
            val = self.meting_level.level()
            try:
                try:
                    self.doc.add_next_tick_callback(
                        functools.partial(self.set_variable_function_probe_0, val)
                    )
                except AttributeError:
                    self.set_variable_function_probe_0(val)
            except AttributeError:
                pass

        def set_above_500M(freqs):
            while self.freq < HARMONIC_THRESHOLD:  # Frequency with less noise
                self.freq += self.px_clocks[self.px_idx]
            freqs.append(self.freq)
            self.set_freq(self.freq)

        def print_and_append_candidates(final_leakage, final_modes, final_freqs):
            print("\nList of most energy leakage:")
            compteur = 0
            for i in final_leakage:
                compteur += 1
                max_index = final_leakage.index(max(final_leakage))
                print(
                    "Mode: "
                    + final_modes[max_index]
                    + "\t | Energy: "
                    + str(final_leakage[max_index])
                    + "\t | Freq: "
                    + str(final_freqs[max_index])
                )
                # print("raw_in_file(final_list[max_index], self.modes[max_index])
                final_leakage[max_index] = -9999.0
                candidate_freqs.append(final_freqs[max_index])
                candidate_modes.append(final_modes[max_index])

        def get_candidates(mean, freqs):
            final_leakage = []
            final_modes = []
            final_freqs = []
            for i in range(len(self.mean_clocks)):
                if self.mean_clocks[i] > mean:
                    final_leakage.append(round(self.mean_clocks[i], 5))
                    final_modes.append(self.modes[i])
                    final_freqs.append(freqs[i])
            return final_leakage, final_modes, final_freqs

        # Main function of the thread, get a list of the most leakage frequencies.
        def _leakage_computation():
            self.freq = self.px_clocks[0]
            nb_measure = 4  # Arbitrary value, measures are relevant
            print("Wait for computation...")

            freqs = []
            # Iterate on the whole set of frequencies
            while self.px_idx < len(self.px_clocks) - 1:

                # Set to an harmonic with less noise
                if self.ctr == 0:
                    set_above_500M(freqs)

                self.ctr += 1

                # Compute energy level
                compute_level()

                # Compute the mean and add it to our list
                if self.ctr > 1 and self.ctr < nb_measure:
                    self.mean += self.get_variable_function_probe_0()
                elif self.ctr == nb_measure:
                    self.mean /= nb_measure - 2
                    if self.verbose:
                        print(
                            str(self.modes[self.px_idx])
                            + "\t:  "
                            + str(self.mean)
                            + "\t ("
                            + str(self.freq)
                            + ")"
                        )
                    self.mean_clocks.append(self.mean)
                    self.mean = 0
                    self.ctr = 0
                    self.px_idx += 1
                    self.freq = self.px_clocks[self.px_idx]
                time.sleep(1 / 20)  # Try winning time here involves measuring errors

            # Choose only the one with most leakage (above the mean + 5% of the mean)
            mean = sum(self.mean_clocks) / len(self.mean_clocks)
            mean = mean - (5 / 100) * mean  # Eliminate candidates that are not above
            if self.verbose:
                print("Mean: " + str(mean))

            final_leakage, final_modes, final_freqs = get_candidates(mean, freqs)

            # Printing in standard output the most leakage and add it to global list
            print_and_append_candidates(final_leakage, final_modes, final_freqs)

            self.stop()
            self.wait()
            Qt.QApplication.quit()

        _variable_function_probe_0_thread = threading.Thread(
            target=_leakage_computation
        )
        _variable_function_probe_0_thread.daemon = True
        _variable_function_probe_0_thread.start()

        ##################################################
        # Connections
        ##################################################
        self.connect((self.osmosdr_source_0, 0), (self.blocks_correctiq_0, 0))
        self.connect((self.blocks_correctiq_0, 0), (self.band_pass_filter_0, 0))
        self.connect(
            (self.band_pass_filter_0, 0), (self.blocks_complex_to_mag_squared_0, 0)
        )
        self.connect(
            (self.blocks_complex_to_mag_squared_0, 0),
            (self.blocks_moving_average_xx_0, 0),
        )
        self.connect((self.blocks_moving_average_xx_0, 0), (self.blocks_nlog10_ff_0, 0))
        self.connect((self.blocks_nlog10_ff_0, 0), (self.meting_level, 0))
        self.connect((self.band_pass_filter_0, 0), (self.qtgui_freq_sink_x_0, 0))

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
        self.set_freq(self.px_rate * self.harmonic)

    def get_harmonic(self):
        return self.harmonic

    def set_harmonic(self, harmonic):
        self.harmonic = harmonic
        self.set_freq(self.px_rate * self.harmonic)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.band_pass_filter_0.set_taps(
            firdes.band_pass(
                1,
                self.samp_rate,
                self.low_cut,
                self.high_cut,
                100000,
                window.WIN_HAMMING,
                6.76,
            )
        )
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.freq, self.samp_rate)

    def get_modes(self):
        return self.modes

    def set_modes(self, modes):
        self.modes = modes

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_source_0.set_center_freq(self.freq, 0)
        # self.qtgui_freq_sink_x_0.set_frequency_range(self.freq, self.samp_rate)

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
        Qt.QMetaObject.invokeMethod(
            self._variable_qtgui_label_0_label,
            "setText",
            Qt.Q_ARG(
                "QString",
                str(
                    self._variable_qtgui_label_0_formatter(self.variable_qtgui_label_0)
                ),
            ),
        )
